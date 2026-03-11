import logging
import pandas as pd

from datetime import datetime, timedelta
from airflow import DAG
from airflow.hooks.postgres_hook import PostgresHook
from airflow.models.baseoperator import BaseOperator
from airflow.models.taskinstance import TaskInstance
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.decorators import apply_defaults
from airflow.utils.task_group import TaskGroup
from airflow.providers.common.sql.sensors.sql import SqlSensor

# Extract
from extract import (
    fetch_html_content, extract_table, save_as_json,
    fetch_csv_content, save_as_csv
)

# Transform
from transform import (
    load_countries_data, add_surrogate_key, rename_columns, standardize_country_names,
    load_earthquake_data, project_columns, convert_time_to_date, save_dataframe_to_csv,
    normalize_location_country,
    load_olympics_data, filter_gold_medals, convert_age_to_numeric,
    normalize_sport_event, add_limit_to_rows
)
# Load
from load import (
    DimCountriesDDL,
    FactEarthquakeDDL,
    DimLocationCountryDDL,
    FactOlympicsDDL,
    DimOlympicsSportEventDDL
)


# Bulk Load Operator
class PostgresBulkLoadOperator(BaseOperator):

    template_fields = ("table_name", "file_path")

    @apply_defaults
    def __init__(self, *, postgres_conn_id: str, table_name: str, file_path: str, **kwargs):
        super().__init__(**kwargs)
        self.postgres_conn_id = postgres_conn_id
        self.table_name = table_name
        self.file_path = file_path

    def execute(self, context):
        hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        try:
            with open(self.file_path, "r") as f:
                columns = f.readline().strip().split(",")
                copy_sql = (
                    f"COPY {self.table_name} ({', '.join(columns)}) "
                    f"FROM STDIN WITH CSV HEADER"
                )
                f.seek(0)
                hook.copy_expert(copy_sql, f.name)
                logging.info(f"Loaded data into '{self.table_name}' from {self.file_path}")
        except FileNotFoundError:
            logging.error(f"File '{self.file_path}' not found.")
            raise
        except Exception as ex:
            logging.error(f"An error occurred while loading data: {ex}")
            raise


# Extract Functions
def extract_countries_dataset(url: str, ti: TaskInstance):
    output_file = f"countries_extracted_{ti.run_id}.json"
    tree = fetch_html_content(url)
    table_data = extract_table(tree)
    save_as_json(table_data, output_file)
    ti.xcom_push(key="countries_dataset_path", value=output_file)

def extract_earthquakes_dataset(url: str, ti: TaskInstance):
    output_file = f"earthquakes_extracted_{ti.run_id}.csv"
    content = fetch_csv_content(url)
    save_as_csv(content, output_file)
    ti.xcom_push(key="earthquake_dataset_path", value=output_file)

def extract_olympics_dataset(url: str, ti: TaskInstance):
    output_file = f"olympics_extracted_{ti.run_id}.csv"
    content = fetch_csv_content(url)
    save_as_csv(content, output_file)
    ti.xcom_push(key="olympics_dataset_path", value=output_file)


# Transform Functions
def transform_countries_dataset(ti: TaskInstance):
    input_file = ti.xcom_pull(task_ids="extract_tasks.extract_countries", key="countries_dataset_path")
    output_file = f"dim_countries_{ti.run_id}.csv"
    df = load_countries_data(input_file)
    df = add_surrogate_key(df, "country_id")
    df = rename_columns(df, {"Country or territory": "country"})
    df = standardize_country_names(df, "country")
    df = df[df["country"].str.lower() != "world"]
    df = df[["country_id", "country"]].reset_index(drop=True)
    df["country_id"] = range(1, len(df) + 1)
    df.to_csv(output_file, index=False)
    ti.xcom_push(key="dim_countries_csv", value=output_file)

def transform_earthquakes_combined(ti: TaskInstance):
    input_file = ti.xcom_pull(task_ids="extract_tasks.extract_earthquakes", key="earthquake_dataset_path")
    fact_output = f"fact_earthquake_{ti.run_id}.csv"
    dim_loc_output = f"dim_location_country_{ti.run_id}.csv"

    df = load_earthquake_data(input_file)
    df = project_columns(df, ["time", "latitude", "longitude", "depth", "mag", "place", "type"])
    df = add_surrogate_key(df, "earthquake_id")
    rename_map = {
        "time": "event_time",
        "depth": "depth_km",
        "mag": "magnitude",
        "place": "location",
        "type": "event_type"
    }
    df = rename_columns(df, rename_map)
    df = convert_time_to_date(df, "event_time")

    merged_df, location_country_df = normalize_location_country(df)
    fact_df = merged_df[["earthquake_id", "event_time", "magnitude", "depth_km",
                         "latitude", "longitude", "location_country_id"]]
    save_dataframe_to_csv(fact_df, fact_output)
    ti.xcom_push(key="earthquake_transformed_csv", value=fact_output)

    location_country_df = location_country_df.rename(columns={"country_extracted": "location"})
    location_country_df = location_country_df[["location_country_id", "location"]]
    location_country_df.to_csv(dim_loc_output, index=False)
    ti.xcom_push(key="dim_location_country_csv", value=dim_loc_output)

def transform_olympics_combined(ti: TaskInstance):
    olympics_input = ti.xcom_pull(task_ids="extract_tasks.extract_olympics", key="olympics_dataset_path")
    countries_csv = ti.xcom_pull(task_ids="transform_tasks.transform_countries", key="dim_countries_csv")
    
    fact_output = f"fact_olympics_{ti.run_id}.csv"
    dim_event_output = f"dim_olympics_sport_event_{ti.run_id}.csv"

    df = load_olympics_data(olympics_input)
    df = project_columns(df, ["id", "name", "sex", "age", "team", "year", "season", "sport", "event", "medal"])
    df = filter_gold_medals(df)  # optional
    df = add_surrogate_key(df, "olympic_record_id")
    df = convert_age_to_numeric(df, "age")
    df, sport_event_df = normalize_sport_event(df)
    df = add_limit_to_rows(df, max_rows=1999)
    df = rename_columns(df, {"name": "athlete_name"})

    cdf = pd.read_csv(countries_csv)
    cdf["country"] = cdf["country"].str.strip()

    df["team"] = df["team"].str.split("/").str[0].str.strip()
    df["olympic_record_id"] = df["olympic_record_id"].astype(int)

    df = df.merge(cdf[["country_id", "country"]], left_on="team", right_on="country", how="left")
    df.drop(columns=["country"], inplace=True)
    df.dropna(subset=["country_id"], inplace=True)
    df["country_id"] = df["country_id"].astype(int)

    fact_df = df[["olympic_record_id", "athlete_name", "age", "year", "medal", "country_id", "sport_event_id"]]
    save_dataframe_to_csv(fact_df, fact_output)
    ti.xcom_push(key="fact_olympics_csv", value=fact_output)

    sport_event_df = sport_event_df[["sport_event_id", "sport", "event"]]
    sport_event_df.to_csv(dim_event_output, index=False)
    ti.xcom_push(key="dim_olympics_sport_event_csv", value=dim_event_output)



# DAG definition
default_args = {
    "owner": "Orkhan",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="etl-workflow-dag",
    default_args=default_args,
    description="ETL Workflow",
    start_date=datetime(2025, 4, 1),
    schedule_interval="0 3 * * *",
    catchup=False,
) as dag:


    # Extract group 
    with TaskGroup("extract_tasks", tooltip="All Extraction Tasks") as extract_group:

        extract_countries = PythonOperator(
            task_id="extract_countries",
            python_callable=extract_countries_dataset,
            op_kwargs={
                "url": "https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"
            },
        )
        extract_earthquakes = PythonOperator(
            task_id="extract_earthquakes",
            python_callable=extract_earthquakes_dataset,
            op_kwargs={
                "url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_week.csv"
            },
        )
        extract_olympics = PythonOperator(
            task_id="extract_olympics",
            python_callable=extract_olympics_dataset,
            op_kwargs={
                "url": "https://raw.githubusercontent.com/rfordatascience/"
                       "tidytuesday/master/data/2021/2021-07-27/olympics.csv"
            },
        )


    # Transform group
    with TaskGroup("transform_tasks", tooltip="All Transformation Tasks") as transform_group:

        transform_countries = PythonOperator(
            task_id="transform_countries",
            python_callable=transform_countries_dataset,
        )
        transform_earthquakes = PythonOperator(
            task_id="transform_earthquakes",
            python_callable=transform_earthquakes_combined,
        )
        transform_olympics = PythonOperator(
            task_id="transform_olympics",
            python_callable=transform_olympics_combined,
        )

        transform_countries >> transform_olympics


    # Load group
    with TaskGroup("load_tasks", tooltip="All Load Tasks") as load_group:

        # Drop
        drop_tables = PostgresOperator(
            task_id="drop_tables",
            postgres_conn_id="postgres_webik",
            sql=f"""
                {DimCountriesDDL.drop_table_query}
                {FactEarthquakeDDL.drop_table_query}
                {DimLocationCountryDDL.drop_table_query}
                {FactOlympicsDDL.drop_table_query}
                {DimOlympicsSportEventDDL.drop_table_query}
            """,
        )

        # Create
        create_tables = PostgresOperator(
            task_id="create_tables",
            postgres_conn_id="postgres_webik",
            sql=f"""
                {DimCountriesDDL.create_table_query}
                {FactEarthquakeDDL.create_table_query}
                {DimLocationCountryDDL.create_table_query}
                {FactOlympicsDDL.create_table_query}
                {DimOlympicsSportEventDDL.create_table_query}
            """,
        )

        # Bulk Load
        def bulk_load_all_callable(ti: TaskInstance):
            hook = PostgresHook(postgres_conn_id="postgres_webik")

            # dim_countries
            dim_countries_csv = ti.xcom_pull(task_ids="transform_tasks.transform_countries", key="dim_countries_csv")
            with open(dim_countries_csv, "r") as f:
                cols = f.readline().strip().split(",")
                sql = f"COPY dim_countries ({', '.join(cols)}) FROM STDIN WITH CSV HEADER"
                f.seek(0)
                hook.copy_expert(sql, f.name)
                logging.info(f"Loaded dim_countries from {dim_countries_csv}")

            # fact_earthquake
            eq_csv = ti.xcom_pull(task_ids="transform_tasks.transform_earthquakes", key="earthquake_transformed_csv")
            with open(eq_csv, "r") as f:
                cols = f.readline().strip().split(",")
                sql = f"COPY fact_earthquake ({', '.join(cols)}) FROM STDIN WITH CSV HEADER"
                f.seek(0)
                hook.copy_expert(sql, f.name)
                logging.info(f"Loaded fact_earthquake from {eq_csv}")

            # dim_location_country
            loc_csv = ti.xcom_pull(task_ids="transform_tasks.transform_earthquakes", key="dim_location_country_csv")
            with open(loc_csv, "r") as f:
                cols = f.readline().strip().split(",")
                sql = f"COPY dim_location_country ({', '.join(cols)}) FROM STDIN WITH CSV HEADER"
                f.seek(0)
                hook.copy_expert(sql, f.name)
                logging.info(f"Loaded dim_location_country from {loc_csv}")

            # fact_olympics
            olympics_csv = ti.xcom_pull(task_ids="transform_tasks.transform_olympics", key="fact_olympics_csv")
            with open(olympics_csv, "r") as f:
                cols = f.readline().strip().split(",")
                sql = f"COPY fact_olympics ({', '.join(cols)}) FROM STDIN WITH CSV HEADER"
                f.seek(0)
                hook.copy_expert(sql, f.name)
                logging.info(f"Loaded fact_olympics from {olympics_csv}")

            # dim_olympics_sport_event
            sport_event_csv = ti.xcom_pull(task_ids="transform_tasks.transform_olympics", key="dim_olympics_sport_event_csv")
            with open(sport_event_csv, "r") as f:
                cols = f.readline().strip().split(",")
                sql = f"COPY dim_olympics_sport_event ({', '.join(cols)}) FROM STDIN WITH CSV HEADER"
                f.seek(0)
                hook.copy_expert(sql, f.name)
                logging.info(f"Loaded dim_olympics_sport_event from {sport_event_csv}")

        bulk_load_all = PythonOperator(
            task_id="bulk_load_all",
            python_callable=bulk_load_all_callable,
        )

        drop_tables >> create_tables >> bulk_load_all


    # Sql sensor to verify data was loaded
    verify_dim_countries = SqlSensor(
        task_id="verify_dim_countries",
        conn_id="postgres_webik",
        sql="SELECT COUNT(*) FROM dim_countries WHERE country IS NOT NULL;",
        poke_interval=30,
        timeout=300,
        mode="poke",
    )

    extract_group >> transform_group >> load_group >> verify_dim_countries
