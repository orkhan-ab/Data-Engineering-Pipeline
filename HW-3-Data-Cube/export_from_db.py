#!/usr/bin/env python3

import pandas as pd
from sqlalchemy import create_engine
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def fetch_data_to_csv(engine_url: str, sql_query: str, output_file: str) -> None:
    try:
        engine = create_engine(engine_url)
        df = pd.read_sql_query(sql_query, engine)
        df.to_csv(output_file, index=False)
        engine.dispose()
        logging.info("Data exported successfully to '%s'", output_file)
    except Exception as e:
        logging.error("Error fetching data to CSV: %s", e)

def main():
    engine_url = 'postgresql://your_username:your_password@your_host:your_port/your_db_name'
    
    sql_query = """
    SELECT
        fact_olympics.olympic_record_id,
        fact_olympics.athlete_name,
        fact_olympics.age,
        fact_olympics.year,
        fact_olympics.medal,
        dim_countries.country,
        dim_olympics_sport_event.sport,
        dim_olympics_sport_event.event
    FROM "public"."fact_olympics"
    JOIN "public"."dim_countries"
      ON "public"."fact_olympics".country_id = "public"."dim_countries".country_id
    JOIN "public"."dim_olympics_sport_event"
      ON "public"."fact_olympics".sport_event_id = "public"."dim_olympics_sport_event".sport_event_id;
    """
    
    output_file = "fact_olympics_raw.csv"
    fetch_data_to_csv(engine_url, sql_query, output_file)

if __name__ == "__main__":
    main()
