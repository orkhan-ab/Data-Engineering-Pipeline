# ETL Data Warehouse Project

In this project I implemen an ETL workflow to process datasets related to Olympics, Earthquakes, and Countries. The goal is to load the transformed data into a PostgreSQL data warehouse, designed using a galaxy schema.

---

## System Requirements

- **Python:** Version 3.8 or later  
- **PostgreSQL:** Version 12 or later (or any compatible version)  
- **Libraries:**  
  - `pandas`
  - `requests`
  - `lxml`
  - `psycopg2`
  - `logging`
  
---

## Installation Instructions

1. **Clone the Repository:**

git clone https://gitlab.mff.cuni.cz/teaching/ndbi046/2024-25/orkhan-abilov.git
cd orkhan-abilov

2. **Install the packages** 

pip install -r requirements.txt

3. **Install PostgreSQL**

Install PostgreSQL if not already installed.

Update the connection credentials in the file connection.json as needed.

Connect to the database using connection.json file


## Description

Both extract.py and transform.py work just by running them 


python .\extract.py
python .\transform.py

For the load part run this command

python load.py connection.json


1. **Extract**

Script: extract.py

Inputs:

URLs for CSV files (e.g., Olympics Medal Winners, Earthquake data)

URL for the Wikipedia page used for web scraping Countries population data

Outputs:

olympics_medal_winners.csv

earthquake_data.csv

list_of_countries_by_population.json

Saved into output folder: extract_output_folder

2. **Transform**

Script: transform.py

Inputs:

Extracted files from the extract_output_folder

Outputs:

olympics_transformed.csv & dim_olympics_sport_event.csv in folder transform_output_olympics

dim_countries.json in folder transform_output_countries

earthquake_transformed.csv & dim_location_country.csv in folder transform_output_earthquake

Additionally there is a join between olympics_transformed.csv and dim_countries.json to reference the country_id for athletes team

3. **Load**

Script: load.py

Inputs:

Transformed and joined files from the transformation part

Connection credentials from connection.json

Outputs:

Data loaded into PostgreSQL tables 


## Workflow explained

The diagram is in the repository called ETLWorkflow_Diagram.svg
Below is the description

1. **Extract**

I downloaded Olympics and Earthquake datasets as CSV files from online sources.

And, extracted the Countries dataset using web scraping from Wikipedia.

I used diffirent methods and data types for variety

2. **Transform**

**Olympics Dataset**

**Input: olympics_medal_winners.csv**
**Output: olympics_transformed.csv and a separate dimension table dim_olympics_sport_event.csv**

Removed extra columns
I kept only the important ones like name, age, team, year, sport, medal, etc. I removed colums like height and weight because they were not needed.

Kept only gold medal winners
I filtered the data to include only the athletes who won gold medals.

Renamed columns
For example, I changed columns names to make it more consistent with other datasets.

Added a unique ID
I added olympic_record_id so that every row has its own identifier. This is useful when putting data into the database.

Converted age to numbers
Some values were stored as text, so I converted age to numbers.

Normalized sport and event
I created a new table dim_sport_event for unique sport and event pairs to avoid repeating them over and over again.

Limited the number of rows
I made sure there were at most 2000 rows.

Cleaned the Team Column and Added Country Reference
Since the team column contains the country name, I cleaned it by splitting country names like "Denmark/Sweden" and taking the first part. Then, I joined this data with the transformed countries data (from dim_countries.json) to add the country_id.
In my data warehouse design, I decided that the fact table for Olympics should reference the dim_country dimension via country_id rather than storing country names.

**Countries Dataset**

**Input: list_of_countries_by_population.json**
**Output: dim_countries.json and dim_region.json**

Fixed the Format:
The original file was in a list-of-lists format. I used the first row as column names and converted the remaining rows into a table.

Renamed Columns:
I renamed column name "Country or territory" to simpler one "country" for consistency.

Cleaned Country Names:
Some country names had extra annotations (such as "[a]"); I removed these to make the names consistent.

Added a Country ID:
I added a surrogate key called country_id to identify each country. After filtering out unwanted records (like "World"), I reassigned the IDs so that the first country becomes 1, the second 2, and so on.

Dropped Region Information
Instead of normalizing region information into a separate dimension (dim_region), I decided to simplify the schema. The final dim_countries table now contains only the needed columns: country_id and country.


**Earthquake Dataset**

**Input: earthquake_data.csv**
**Output: earthquake_transformed.csv and dim_location_country.csv**

Removed extra columns
I selected only the columns that are needed: time, latitude, longitude, depth, mag, place, and type.

Id
I added an earthquake_id to identify each earthquake event.

Formatted the date
I renamed columns to make them more understandable (time to event_time, mag to magnitude, etc.) and converted the event_time to only show the date (YYYY-MM-DD).

Converted values to numbers
I made sure magnitude and depth were stored as numbers.

Extracted country from place
The place column had useless text like "100 km SE of Jakarta, Indonesia". I extracted just the country part ("Indonesia").

Initially, I created a separate dimension table (dim_location_country) from the earthquake data to store location names and assigned a surrogate key (location_country_id).
Since some locations (like "South Sandwich Islands") might not be in dim_countries, this keeps the earthquake facts separate while still referencing a location dimension.


3. **Load**

In the Load part, I took the transformed data from the previous steps and inserted it into my PostgreSQL data warehouse. I set up my database tables according to the design of my data warehouse schema galaxy design.

I read the connection details from a JSON file connection.json.

For each table in my warehouse (for example, dim_countries, fact_olympics, fact_earthquake, dim_olympics_sport_event, and dim_location_country), I wrote SQL DDL (Data Definition Language) statements to drop any existing tables and then create new ones with the proper structure.

For dimensions, I defined columns like country_id, country, and region_ref.

For fact tables, I defined primary keys and the columns that store measures (such as age, year, medal for Olympics or magnitude, depth for earthquakes).

Bulk Loading Data:
I used Python with the psycopg2 library to bulk insert data from the transformed CSV and JSON files into the created tables.

I also used the execute_values function to insert multiple rows at once.

After all data was loaded, I executed ALTER TABLE statements to add primary key constraints.

Once the load process was done, I made sure the data in PostgreSQL using DBeaver programm by running SELECT queries.



## Warehouse UML schema

I designed my warehouse using a galaxy schema. In this schema, I have two fact tables that have their own specific dimensions.

The schema is in WarehouseUML.svg file inside of the repository

**Fact Tables:**

**fact_olympics**

Stores Olympic event records.

olympic_record_id (PK): A unique id for each Olympic record.
age: The athlete’s age.
year: The year of the Olympic event.
medal: The type of medal won (in this case I left only gold medals).
sport_event_id (FK): References the sport and event from a dimension table.
country_id (FK): References the country from which the athlete represents.

**fact_earthquake**

Stores records for each earthquake event.

earthquake_id: Unique id for each earthquake.
event_time: The date of the earthquake.
magnitude: The earthquake’s magnitude.
depth_km: The depth of the earthquake.
latitude/longitude: Geographic coordinates.
location_country_id: References the location dimension for earthquake data.

**Dimension Tables**

**dim_countries**

Contains countries and their ids.

country_id: A surrogate key uniquely identifying each country.
country: The country name.

This table is referenced by fact_olympics to indicate which country an athlete represents.

**dim_olympics_sport_event**

Contains sports and events the athletes performed.

sport_event_id: A surrogate key for each sport–event pair.
sport: The sport name.
event: The event name.

fact_olympics references this table via sport_event_id to avoid not record sport and event names multiple times.

**dim_location_country**

Contains location information from earthquake data.

location_country_id: A unique id for each location.
location: The name of the location.

fact_earthquake uses this table (through location_country_id) because some earthquake locations might not match the country names in dim_countries.


**Galaxy Schema:**

The overall design is a galaxy schema because I have two fact tables (fact_olympics and fact_earthquake) that have dimensions.

