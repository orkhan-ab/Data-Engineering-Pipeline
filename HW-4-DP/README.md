## ETL Provenance

System Requirements
Python 3.8+
rdflib 
pandas


## Installation
Clone my repository 

git clone https://gitlab.mff.cuni.cz/teaching/ndbi046/2024-25/orkhan-abilov.git

pip install rdflib pandas


## Description

data_provenance.py

This script creates a provenance document describing ETL workflow and data‑cube construction in RDF,TriG, using the PROV‑O ontology.

Defines entities for datasets, tables (DimCountries, FactOlympics, etc.) and the AnalyticalDataCube.

Defines agents (myself, Apache Airflow, the Python script, MFF UK, GitHub, USGS, Wikipedia).

Defines activities (ETL steps and the cube construction), linking them to inputs using prov:used, prov:qualifiedUsage, and prov:qualifiedAssociation.

Output

A Prov document in TriG format:

python data_provenance.py output.trig

