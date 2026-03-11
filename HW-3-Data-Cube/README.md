## System Requirements

Python: version 3.8 or higher

PostgreSQL: Access to a PostgreSQL 


## Installation 

Clone the repository 

git clone https://gitlab.mff.cuni.cz/teaching/ndbi046/2024-25/orkhan-abilov.git

Install required packages:

pip install pandas sqlalchemy psycopg2-binary rdflib


## Script Files

1. export_from_db.py

Here I extract data from the database and write it to a CSV file.

Make sure to change the credentials to connect to the databse ('postgresql://your_username:your_password@your_host:your_port/your_db_name')

Usage:

python export_from_db.py

Input:

SQL query joining three tables: public.fact_olympics, public.dim_countries, public.dim_olympics_sport_event

Output:

fact_olympics_raw.csv in the directory


2. datacube_fixed.py

This script reads the CSV file and creates an RDF Data Cube.

Usage:

python datacube_fixed.py

Inputs:

fact_olympics_raw.csv (exported by export.py)

Outputs:

datacube.ttl: RDF Data Cube in Turtle


3. check-well-formed.py

This script validates the RDF Data Cube against integrity constraints.

Usage:

python check-well-formed.py datacube.ttl

Inputs:

datacube.ttl

Outputs:

Console output saying PASSED