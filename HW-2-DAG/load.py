import sys
import json
import logging
import pandas as pd
import psycopg2
from psycopg2 import connect, Error
from psycopg2.extras import execute_values
from typing import Dict, Any
import os

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def read_config_file(config_file: str) -> Dict[str, Any]:
    try:
        with open(config_file, "r") as file:
            config = json.load(file)
        return config
    except Exception as e:
        logging.error(f"Error reading config file: {e}")
        raise

def read_json_data(file_path: str) -> pd.DataFrame:
    try:
        df = pd.read_json(file_path, orient="records")
        return df
    except Exception as e:
        logging.error(f"Error reading JSON data: {e}")
        raise

def read_csv_data(file_path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(file_path, dtype=str)
        return df
    except Exception as e:
        logging.error(f"Error reading CSV data: {e}")
        raise

def execute_ddl(conn_params: Dict[str, Any], ddl_statement: str) -> None:
    conn = None
    cur = None
    try:
        conn = connect(**conn_params)
        cur = conn.cursor()
        cur.execute(ddl_statement)
        conn.commit()
    except Error as e:
        logging.error(f"Error executing DDL: {e}")
        raise
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

def insert_data_bulk(conn_params: Dict[str, Any], insert_query: str, data_df: pd.DataFrame) -> None:
    conn = None
    cur = None
    try:
        conn = connect(**conn_params)
        cur = conn.cursor()
        data_tuples = list(data_df.itertuples(index=False, name=None))
        execute_values(cur, insert_query, data_tuples)
        conn.commit()
    except Error as e:
        logging.error(f"Error inserting data: {e}")
        raise
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()


# dim_countries
class DimCountriesDDL:
    drop_table_query = "DROP TABLE IF EXISTS dim_countries;"
    create_table_query = """
    CREATE TABLE dim_countries (
        country_id INT,
        country VARCHAR(255),
        PRIMARY KEY (country_id)
    );
    """
    insert_query = """
    INSERT INTO dim_countries (country_id, country)
    VALUES %s;
    """


# fact_olympics
class FactOlympicsDDL:
    drop_table_query = "DROP TABLE IF EXISTS fact_olympics;"
    create_table_query = """
    CREATE TABLE fact_olympics (
        olympic_record_id INTEGER,
        athlete_name      VARCHAR(255),
        age               NUMERIC,
        year              INTEGER,
        medal             VARCHAR(50),
        country_id        INT,
        sport_event_id    INT,
        PRIMARY KEY (olympic_record_id)
    );
    """
    insert_query = """
    INSERT INTO fact_olympics (
        olympic_record_id, athlete_name, age, year, medal, country_id, sport_event_id
    ) VALUES %s;
    """


# fact_earthquake
class FactEarthquakeDDL:
    drop_table_query = "DROP TABLE IF EXISTS fact_earthquake;"
    create_table_query = """
    CREATE TABLE fact_earthquake (
        earthquake_id  INT,
        event_time     DATE,
        magnitude      NUMERIC,
        depth_km       NUMERIC,
        latitude       NUMERIC,
        longitude      NUMERIC,
        location_country_id INT,
        PRIMARY KEY (earthquake_id)
    );
    """
    insert_query = """
    INSERT INTO fact_earthquake (
        earthquake_id, event_time, magnitude, depth_km, latitude, longitude, location_country_id
    ) VALUES %s;
    """


# dim_location_country
class DimLocationCountryDDL:
    drop_table_query = "DROP TABLE IF EXISTS dim_location_country;"
    create_table_query = """
    CREATE TABLE dim_location_country (
        location_country_id INT,
        location VARCHAR(255),
        PRIMARY KEY (location_country_id)
    );
    """
    insert_query = """
    INSERT INTO dim_location_country (location_country_id, location)
    VALUES %s;
    """


# dim_olympics_sport_event
class DimOlympicsSportEventDDL:
    drop_table_query = "DROP TABLE IF EXISTS dim_olympics_sport_event;"
    create_table_query = """
    CREATE TABLE dim_olympics_sport_event (
        sport_event_id INT,
        sport VARCHAR(255),
        event VARCHAR(255),
        PRIMARY KEY (sport_event_id)
    );
    """
    insert_query = """
    INSERT INTO dim_olympics_sport_event (sport_event_id, sport, event)
    VALUES %s;
    """


def main():
    if len(sys.argv) != 2:
        logging.error("Usage: python load.py <config_file>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    conn_params = read_config_file(config_file)
    
    # Load dim_countries
    try:
        countries_file = os.path.join("transform_output_countries", "dim_countries.json")
        df_countries = read_json_data(countries_file)
        
        expected_countries_cols = ["country_id", "country"]
        df_countries = df_countries[expected_countries_cols]
        
        df_countries = df_countries.reset_index(drop=True)
        df_countries["country_id"] = range(1, len(df_countries) + 1)
        
        execute_ddl(conn_params, DimCountriesDDL.drop_table_query)
        execute_ddl(conn_params, DimCountriesDDL.create_table_query)
        insert_data_bulk(conn_params, DimCountriesDDL.insert_query, df_countries)
        
        logging.info("dim_countries loaded successfully (minimal version).")
    except Exception as e:
        logging.error(f"Error loading dim_countries: {e}")
    

    # Load fact_olympics
    try:
        olympics_file = os.path.join("transform_output_olympics", "olympics_transformed.csv")
        df_olympics = read_csv_data(olympics_file)
        
        expected_fact_cols = ["olympic_record_id", "athlete_name", "age", "year", "medal", "country_id", "sport_event_id"]
        df_olympics = df_olympics[expected_fact_cols]
        
        execute_ddl(conn_params, FactOlympicsDDL.drop_table_query)
        execute_ddl(conn_params, FactOlympicsDDL.create_table_query)
        insert_data_bulk(conn_params, FactOlympicsDDL.insert_query, df_olympics)
        
        logging.info("fact_olympics loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading fact_olympics: {e}")
    

    # Load fact_earthquake 
    try:
        earthquake_file = os.path.join("transform_output_earthquake", "earthquake_transformed.csv")
        df_eq = read_csv_data(earthquake_file)
        expected_eq_cols = ["earthquake_id", "event_time", "magnitude", "depth_km", "latitude", "longitude", "location_country_id"]
        df_eq = df_eq[expected_eq_cols]
        
        execute_ddl(conn_params, FactEarthquakeDDL.drop_table_query)
        execute_ddl(conn_params, FactEarthquakeDDL.create_table_query)
        insert_data_bulk(conn_params, FactEarthquakeDDL.insert_query, df_eq)
        
        logging.info("fact_earthquake loaded.")
    except Exception as e:
        logging.error(f"Error loading fact_earthquake: {e}")


    # Load dim_location_country
    try:
        loc_country_file = os.path.join("transform_output_earthquake", "dim_location_country.csv")
        df_loc_country = read_csv_data(loc_country_file)
        df_loc_country = df_loc_country.rename(columns={"country_extracted": "location"})
        expected_cols = ["location_country_id", "location"]
        df_loc_country = df_loc_country[expected_cols]
        
        execute_ddl(conn_params, DimLocationCountryDDL.drop_table_query)
        execute_ddl(conn_params, DimLocationCountryDDL.create_table_query)
        insert_data_bulk(conn_params, DimLocationCountryDDL.insert_query, df_loc_country)
        
        logging.info("dim_location_country loaded.")
    except Exception as e:
        logging.error(f"Error loading dim_location_country: {e}")

    
    # Load dim_olympics_sport_event 
    try:
        sport_event_file = os.path.join("transform_output_olympics", "dim_olympics_sport_event.csv")
        df_sport_event = read_csv_data(sport_event_file)
        
        expected_cols = ["sport_event_id", "sport", "event"]
        df_sport_event = df_sport_event[expected_cols]
        
        execute_ddl(conn_params, DimOlympicsSportEventDDL.drop_table_query)
        execute_ddl(conn_params, DimOlympicsSportEventDDL.create_table_query)
        insert_data_bulk(conn_params, DimOlympicsSportEventDDL.insert_query, df_sport_event)
        
        logging.info("dim_olympics_sport_event loaded.")
    except Exception as e:
        logging.error(f"Error loading dim_olympics_sport_event: {e}")


if __name__ == "__main__":
    main()
