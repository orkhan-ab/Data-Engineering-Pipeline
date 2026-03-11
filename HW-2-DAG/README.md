## Apache Airflow ETL Workflow
In this repository I have Apache Airflow ETL pipeline that extracts, transforms, and loads data (Countries, Earthquakes, Olympics) into a PostgreSQL database. The workflow is decomposed into separate tasks using TaskGroups, uses a custom bulk load operator, uses XCom for data sharing, and includes a SQL sensor to verify data load.


# System Requirements

Docker is used to package and run the Airflow instance.

Python 3.8 or Later

PostgreSQL Database Server


# Installation 
1. Build the Docker Image

Open a terminal in the project root directory and build the Docker image:

- docker build . --tag mff/airflow:latest


2. Create folders for DAGs, logs, plugins, and configuration files:

- On Linux mkdir -p ./dags ./logs ./plugins ./config 
- On Windows mkdir -p dags, logs, plugins, config


3. Run the Airflow

Run the command to set up the environment:

- docker compose up airflow-init


4. Start Airflow

Start the Airflow containers:

- docker compose up


5. Place DAG Scripts

Copy the dag.py, extract.py, transform.py, and load.py files into the dags folder. Airflow will load these DAGs when it starts.



# Set Up Connection

Before running the ETL DAG, set up PostgreSQL connection in Airflow:

Open web browser and navigate to:

- http://127.0.0.1:8080/

Log in with credentials.
- Login: airflow
- Password: airflow

Go to Admin -> Connections -> Click + to add a new connection.

Enter the details:

Connection Id: postgres_webik

Connection Type: Postgres

Host: webik.ms.mff.cuni.cz

Database: ndbi046

Login: your username

Password: your password

Port: 5432

Save the connection.


Once the Airflow web server is running, navigate to the DAGs section.

Press the trigger button.

Open the Graph View to see how the tasks are grouped and how data flows.


# Explanation

1. Extract:
I created tasks to fetch data from three sources:

Countries: I download an HTML page from Wikipedia, extract the table, and save it as a JSON file.

Earthquakes: I download a CSV file from USGS and save it locally.

Olympics: I download a CSV file from GitHub and save it.

I used PythonOperators to do this and pass the file paths to the next phase with XCom (push method).


2. Transform:
I built tasks to process the files:

First I pull the files using Xcom then,

For Countries, I load the JSON, add a surrogate key, clean up and rename the columns, and save the result as a CSV.

For Earthquakes, I load the CSV, select and rename the columns, convert the date, and then call my normalize_location_country() function. This gives me two files: one for the fact table and one for the dimension table for location data.

For Olympics, I load the CSV, filter the data, add surrogate keys, and merge this data with the Countries data to get the country ID. This gives two CSVs: a fact table and a sport event dimension table.

All of these tasks are also PythonOperators that send their output file paths via XCom (push method).

3. Load:

Drop Tables: I run SQL command to drop all my tables.

Create Tables: I run SQL command to create all the tables.

Bulk Load All: I use a PythonOperator that pulls all the CSV file paths from XCom and uses PostgreSQL’s COPY command to load the data into the database.

Sensor:
I added a SQL sensor at the end of the load group to check that data has been loaded into one table. This sensor waits until there is data in the table before the DAG run finishes.

I put my tasks in groups using TaskGroups so that everything is divided into Extract, Transform, and Load phases. First extract, then transform, then load. Finally, the SQL sensor makes sure my data is loaded.
