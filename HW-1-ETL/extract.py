import csv
import json
import logging
import sys
from typing import List
import os
import requests
from lxml import html

# Logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Csv fetching
def fetch_csv_content(url: str) -> bytes:
    try:
        logging.info(f"Fetching CSV from {url}")
        response = requests.get(url)
        response.raise_for_status()  
        return response.content
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching CSV from {url}: {e}")
        sys.exit(1)

# Web scaping
def fetch_html_content(url: str) -> html.HtmlElement:
    try:
        logging.info(f"Fetching HTML content from {url}")
        response = requests.get(url)
        response.raise_for_status()
        return html.fromstring(response.content)
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching URL: {e}")
        sys.exit(1)

def extract_table(tree: html.HtmlElement) -> List[List[str]]:
    try:
        tables = tree.xpath("//table")
        if not tables:
            logging.error("No tables")
            sys.exit(1)
        rows = tables[0].xpath(".//tr")
        table_data = []
        for row in rows:
            data = [cell.text_content().strip() for cell in row.xpath(".//th | .//td")]
            table_data.append(data)
        return table_data
    except Exception as e:
        logging.error(f"Error with table: {e}")
        sys.exit(1)


# Save data
def save_as_csv(data: bytes, filename: str) -> None:
    try:
        with open(filename, "wb") as f:
            f.write(data)
    except Exception as e:
        logging.error(f"Error saving data as CSV file: {e}")
        raise

def save_as_json(data: List[List[str]], filename: str) -> None:
    try:
        with open(filename, "w", encoding="utf-8") as jsonfile:
            json.dump(data, jsonfile, ensure_ascii=False, indent=4)
        logging.info(f"Data saved to {filename}")
    except Exception as e:
        logging.error(f"Error saving JSON file: {e}")
        sys.exit(1)

# Main
def main():

    output_folder = "extract_output_folder"
    os.makedirs(output_folder, exist_ok=True)

    # Csv Dataset 1: Olympics Medal Winners
    olympics_url = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2021/2021-07-27/olympics.csv"
    olympics_output = os.path.join(output_folder, "olympics_medal_winners.csv")
    olympics_input = fetch_csv_content(olympics_url)
    save_as_csv(olympics_input, olympics_output)
    logging.info(f"Olympics data saved to {olympics_output}")

 
    # Csv Dataset 2: Earthquake Dataset
    earthquake_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_week.csv"
    earthquake_output = os.path.join(output_folder, "earthquake_data.csv")
    earthquake_input = fetch_csv_content(earthquake_url)
    save_as_csv(earthquake_input, earthquake_output)
    logging.info(f"Earthquake data saved {earthquake_output}")

    # Web Scraping Population Dataset In json
    countries_pop = "https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"
    tree = fetch_html_content(countries_pop)
    table_data = extract_table(tree)
    countries_pop_json = os.path.join(output_folder, "list_of_countries_by_population.json")
    save_as_json(table_data, countries_pop_json)
    logging.info(f"Population data saved {countries_pop_json}")

if __name__ == "__main__":
    main()
