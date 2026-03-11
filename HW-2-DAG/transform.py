import pandas as pd
import logging
import json
import os

# Logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Loading datasets
def load_olympics_data(csv_path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        logging.error(f"Error loading CSV file: {e}")
        raise

def load_countries_data(file_path: str) -> pd.DataFrame:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        header = data[0]
        rows = data[1:]
        df = pd.DataFrame(rows, columns=header)
        return df
    except Exception as e:
        logging.error(f"Error loading JSON file: {e}")
        raise

def load_earthquake_data(csv_path: str) -> pd.DataFrame:

    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        logging.error(f"Error loading earthquake CSV file: {e}")
        raise



# Transformations
def project_columns(dataframe: pd.DataFrame, columns: list) -> pd.DataFrame:
    try:
        return dataframe[columns]
    except Exception as e:
        logging.error(f"Error projecting columns: {e}")
        raise

def add_limit_to_rows(df: pd.DataFrame, max_rows: int = 1999) -> pd.DataFrame:
    return df.head(max_rows)

def add_surrogate_key(dataframe: pd.DataFrame, key_name: str) -> pd.DataFrame:
    try:
        dataframe[key_name] = range(1, len(dataframe) + 1)
        return dataframe
    except Exception as e:
        logging.error(f"Error adding surrogate key: {e}")
        raise

def rename_columns(dataframe: pd.DataFrame, column_mapping: dict) -> pd.DataFrame:
    try:
        return dataframe.rename(columns=column_mapping, copy=False)
    except Exception as e:
        logging.error(f"Error renaming columns: {e}")
        raise

def filter_gold_medals(dataframe: pd.DataFrame) -> pd.DataFrame:
    try:
        filtered_df = dataframe[dataframe['medal'].str.strip().str.lower() == 'gold']
        return filtered_df
    except Exception as e:
        logging.error(f"Error filtering gold medals: {e}")
        raise

def standardize_country_names(dataframe: pd.DataFrame, column: str) -> pd.DataFrame:
    try:
        dataframe[column] = dataframe[column].str.replace(r'\[.*\]', '', regex=True).str.strip()
        return dataframe
    except Exception as e:
        logging.error(f"Error standardizing country names: {e}")
        raise

def convert_age_to_numeric(dataframe: pd.DataFrame, column: str = "age") -> pd.DataFrame:
    try:
        dataframe[column] = pd.to_numeric(dataframe[column], errors='coerce')
        return dataframe
    except Exception as e:
        logging.error(f"Error converting '{column}' to numeric: {e}")
        raise

def normalize_sport_event(dataframe: pd.DataFrame) -> (pd.DataFrame, pd.DataFrame):
    try:
        norm_df = dataframe[['sport', 'event']].drop_duplicates().reset_index(drop=True)
        norm_df['sport_event_id'] = range(1, len(norm_df) + 1)

        merged_df = dataframe.merge(norm_df, on=['sport', 'event'], how='left')
        merged_df = merged_df.drop(columns=['sport', 'event'])
        return merged_df, norm_df
    except Exception as e:
        logging.error(f"Error normalizing sport and event columns: {e}")
        raise


def convert_time_to_date(dataframe: pd.DataFrame, column: str = "event_time") -> pd.DataFrame:
    try:
        dataframe[column] = pd.to_datetime(dataframe[column]).dt.strftime("%Y-%m-%d")
        return dataframe
    
    except Exception as e:
        logging.error(f"Error converting {column} to date: {e}")
        raise


def extract_country_from_location(location: str) -> str:
    try:
        if ',' in location:
            return location.split(',')[-1].strip()
        else:
            return location.strip()
        
    except Exception as e:
        logging.error(f"Error extracting country from '{location}': {e}")
        raise

def normalize_location_country(dataframe: pd.DataFrame) -> (pd.DataFrame, pd.DataFrame):
    try:
        dataframe['country_extracted'] = dataframe['location'].apply(extract_country_from_location)
        country_df = dataframe[['country_extracted']].drop_duplicates().reset_index(drop=True)
        country_df['location_country_id'] = range(1, len(country_df) + 1)

        merged_df = pd.merge(dataframe, country_df, on='country_extracted', how='left')

        return merged_df, country_df
    except Exception as e:
        logging.error(f"Error normalizing location country: {e}")
        raise    

def save_dataframe_to_csv(dataframe: pd.DataFrame, file_path: str) -> None:
    try:
        dataframe.to_csv(file_path, index=False)
    except Exception as e:
        logging.error(f"Error saving DataFrame to CSV: {e}")
        raise


if __name__ == "__main__":

    # Countries Dataset
    countries_json_path = os.path.join("extract_output_folder", "list_of_countries_by_population.json")
    countries_output_folder = "transform_output_countries"
    os.makedirs(countries_output_folder, exist_ok=True)
    transformed_countries_json = os.path.join(countries_output_folder, "dim_countries.json")

    try:
        countries_df = load_countries_data(countries_json_path)
        countries_df = add_surrogate_key(countries_df, "country_id")
        rename_map = {
            "Country or territory": "country"
        }
        countries_df = rename_columns(countries_df, rename_map)
        countries_df = standardize_country_names(countries_df, "country")
        countries_df = countries_df[countries_df["country"].str.lower() != "world"]
        countries_df = countries_df[["country_id", "country"]]
        countries_df = countries_df.reset_index(drop=True)
        countries_df["country_id"] = range(1, len(countries_df) + 1)

        countries_df.to_json(transformed_countries_json, orient="records", indent=4)
        
    except Exception as e:
        logging.error(f"Error in transformation pipeline (Countries): {e}")

    # Olympics Dataset
    olympics_input_csv = os.path.join("extract_output_folder", "olympics_medal_winners.csv")
    olympics_output_folder = "transform_output_olympics"
    os.makedirs(olympics_output_folder, exist_ok=True)
    olympics_output_csv = os.path.join(olympics_output_folder, "olympics_transformed.csv")
    sport_event_output_csv = os.path.join(olympics_output_folder, "dim_olympics_sport_event.csv")
    
    try:
        df_olympics = load_olympics_data(olympics_input_csv)
        df_olympics = project_columns(df_olympics, [
            "id", "name", "sex", "age", "team",
            "year", "season", "sport", "event", "medal"
        ])

        df_olympics = filter_gold_medals(df_olympics)
        df_olympics = add_surrogate_key(df_olympics, "olympic_record_id")
        df_olympics = convert_age_to_numeric(df_olympics, "age")
        df_olympics, sport_event_df = normalize_sport_event(df_olympics)
        df_olympics = add_limit_to_rows(df_olympics, max_rows=1999)
        df_olympics = rename_columns(df_olympics, {"name": "athlete_name"})

        countries_file = os.path.join("transform_output_countries", "dim_countries.json")
        countries_df = pd.read_json(countries_file, orient="records")
        countries_df["country"] = countries_df["country"].str.strip()

        # If the team name contains a slash (e.g., "Denmark/Sweden"), take only the first part.
        df_olympics["team"] = df_olympics["team"].str.split("/").str[0].str.strip()
        df_olympics["olympic_record_id"] = df_olympics["olympic_record_id"].astype(int)

        countries_file = os.path.join("transform_output_countries", "dim_countries.json")
        countries_df = pd.read_json(countries_file, orient="records")
        countries_df["country"] = countries_df["country"].str.strip()

        # Join the Olympics data with the countries data on the country name
        df_olympics = df_olympics.merge(
            countries_df[["country", "country_id"]],
            left_on="team",
            right_on="country",
            how="left"
        )

        df_olympics.drop(columns=["country"], inplace=True)

        # Remove rows with missing country_id
        df_olympics = df_olympics.dropna(subset=["country_id"])
        df_olympics["country_id"] = df_olympics["country_id"].astype(int)

        save_dataframe_to_csv(df_olympics, olympics_output_csv)
        save_dataframe_to_csv(sport_event_df, sport_event_output_csv)

    except Exception as e:
        logging.error(f"Failed to process the Olympics data: {e}")
    
    # Earthquakes Dataset
    earthquake_input_csv = os.path.join("extract_output_folder", "earthquake_data.csv")
    earthquake_output_folder = "transform_output_earthquake"
    os.makedirs(earthquake_output_folder, exist_ok=True)
    earthquake_transformed_csv = os.path.join(earthquake_output_folder, "earthquake_transformed.csv")
    location_country_output_csv = os.path.join(earthquake_output_folder, "dim_location_country.csv")
    
    try:
        df_earthquake = load_olympics_data(earthquake_input_csv)
        df_earthquake = project_columns(df_earthquake, ["time", "latitude", "longitude", "depth", "mag", "place", "type"])
        df_earthquake = add_surrogate_key(df_earthquake, "earthquake_id")
        rename_map_eq = {
            "time": "event_time",
            "depth": "depth_km",
            "mag": "magnitude",
            "place": "location",
            "type": "event_type"
        }
        df_earthquake = rename_columns(df_earthquake, rename_map_eq)
        df_earthquake = convert_time_to_date(df_earthquake, "event_time")
        df_earthquake, location_country_df = normalize_location_country(df_earthquake)
        
        save_dataframe_to_csv(df_earthquake, earthquake_transformed_csv)
        save_dataframe_to_csv(location_country_df, location_country_output_csv)

    except Exception as e:
        logging.error(f"Error transforming earthquake data: {e}")

    logging.info("Data transformed, it works")
