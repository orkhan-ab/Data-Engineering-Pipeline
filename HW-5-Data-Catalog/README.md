# Olympics Data Cube Catalog

I created a data catalog using the DCAT standard for my dataset from (Olympics fact table and its RDF data cube).

## System Requirements

- Python 3.7 or higher
- rdflib library

pip install rdflib


Installation and Setup

Clone project folder.

Run the catalog script to generate the catalog description.

## Script Descriptions

1. catalog.py

This script creates the data catalog description in RDF Turtle format.
I used rdflib to define a catalog with:

One dataset (my Olympics data cube)

Two distributions: one for the original CSV and one for the RDF Turtle

Metadata like keywords, themes, publisher (university), creator (me), file size, format, license, and more

Input:

References to fact_olympics_raw.csv and output.ttl

Output:
A Turtle file describing the catalog

Usage:

python catalog.py olympics_catalog.ttl

2. query.py

This script loads the Turtle catalog and runs 2 SPARQL queries over it.

Query 1:
Shows all datasets with their title, issued date, and contact email.

Query 2:
Lists all data distributions with their media type and format.

Input:
Turtle file (e.g., olympics_catalog.ttl)

Output:
Printed results of the two queries

Usage:

python query_catalog.py olympics_catalog.ttl