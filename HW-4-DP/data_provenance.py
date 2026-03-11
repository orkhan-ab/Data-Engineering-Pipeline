#!/usr/bin/env python3

from rdflib import Graph, Literal, Namespace, URIRef, BNode
from rdflib.namespace import RDF, FOAF, XSD, PROV
import logging, sys

olympics_url = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2021/2021-07-27/olympics.csv"
earthquake_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_week.csv"
countries_pop_url = "https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"

NS = Namespace("https://ksi.mff.cuni.cz/~orkhan/232-NDBI046#")

def create_prov_data() -> Graph:
    result = Graph()
    result.bind("", NS)
    result.bind("rdf", RDF)
    result.bind("foaf", FOAF)
    result.bind("xsd", XSD)
    result.bind("prov", PROV)

    create_entities(result)
    create_agents(result)
    create_activities(result)

    return result


def create_entities(collector: Graph) -> None:
    # Olympics CSV
    olympics = NS.OlympicsData
    collector.add((olympics, RDF.type, PROV.Entity))
    collector.add((olympics, PROV.atLocation, Literal(olympics_url, datatype=XSD.anyURI)))
    collector.add((olympics, PROV.wasAttributedTo, NS.GitHub))

    # Earthquake CSV
    earthquake = NS.EarthquakeData
    collector.add((earthquake, RDF.type, PROV.Entity))
    collector.add((earthquake, PROV.atLocation, Literal(earthquake_url, datatype=XSD.anyURI)))
    collector.add((earthquake, PROV.wasAttributedTo, NS.USGS))

    # Countries population page
    countries = NS.CountriesPopData
    collector.add((countries, RDF.type, PROV.Entity))
    collector.add((countries, PROV.atLocation, Literal(countries_pop_url, datatype=XSD.anyURI)))
    collector.add((countries, PROV.wasAttributedTo, NS.Wikipedia))

    # DimCountries
    dim_countries = NS.DimCountries
    collector.add((dim_countries, RDF.type, PROV.Entity))
    collector.add((dim_countries, PROV.wasGeneratedBy, NS.ApacheAirflowActivity))
    collector.add((dim_countries, PROV.hadPrimarySource, NS.CountriesPopData))
    collector.add((dim_countries, PROV.wasAttributedTo, NS.OrkhanAbilov))

    # FactOlympics
    fact_olympics = NS.FactOlympics
    collector.add((fact_olympics, RDF.type, PROV.Entity))
    collector.add((fact_olympics, PROV.wasGeneratedBy, NS.ApacheAirflowActivity))
    collector.add((fact_olympics, PROV.hadPrimarySource, NS.OlympicsData))
    collector.add((fact_olympics, PROV.wasAttributedTo, NS.OrkhanAbilov))

    # FactEarthquake
    fact_earthquake = NS.FactEarthquake
    collector.add((fact_earthquake, RDF.type, PROV.Entity))
    collector.add((fact_earthquake, PROV.wasGeneratedBy, NS.ApacheAirflowActivity))
    collector.add((fact_earthquake, PROV.hadPrimarySource, NS.EarthquakeData))
    collector.add((fact_earthquake, PROV.wasAttributedTo, NS.OrkhanAbilov))

    # DimLocationCountry
    dim_location = NS.DimLocationCountry
    collector.add((dim_location, RDF.type, PROV.Entity))
    collector.add((dim_location, PROV.wasGeneratedBy, NS.ApacheAirflowActivity))
    collector.add((dim_location, PROV.hadPrimarySource, NS.EarthquakeData))
    collector.add((dim_location, PROV.wasAttributedTo, NS.OrkhanAbilov))

    # DimOlympicsSportEvent
    dim_sport_event = NS.DimOlympicsSportEvent
    collector.add((dim_sport_event, RDF.type, PROV.Entity))
    collector.add((dim_sport_event, PROV.wasGeneratedBy, NS.ApacheAirflowActivity))
    collector.add((dim_sport_event, PROV.hadPrimarySource, NS.OlympicsData))
    collector.add((dim_sport_event, PROV.wasAttributedTo, NS.OrkhanAbilov))

    # Data Cube
    data_cube = NS.DataCube
    collector.add((data_cube, RDF.type, PROV.Entity))
    collector.add((data_cube, PROV.wasGeneratedBy, NS.DataCubeActivity))
    collector.add((data_cube, PROV.hadPrimarySource, NS.FactOlympics))
    collector.add((data_cube, PROV.hadPrimarySource, NS.DimCountries))
    collector.add((data_cube, PROV.hadPrimarySource, NS.DimOlympicsSportEvent))
    collector.add((data_cube, PROV.wasAttributedTo, NS.OrkhanAbilov))
 


def create_agents(collector: Graph) -> None:
    # Apache Airflow
    apache_airflow = NS.ApacheAirflow
    collector.add((apache_airflow, RDF.type, PROV.SoftwareAgent))
    collector.add((apache_airflow, RDF.type, PROV.Agent))
    collector.add((apache_airflow, PROV.actedOnBehalfOf, NS.OrkhanAbilov))
    collector.add((apache_airflow, FOAF.name, Literal("Apache Airflow", lang="en")))

    # ETL Script
    etl_script = NS.ETLScript
    collector.add((etl_script, RDF.type, PROV.SoftwareAgent))
    collector.add((etl_script, PROV.actedOnBehalfOf, NS.OrkhanAbilov))
    collector.add((etl_script, FOAF.name, Literal("ETL Python Script", lang="en")))

    # Data Cube Script
    cube_script = NS.CubeBuilderScript         
    collector.add((cube_script, RDF.type, PROV.SoftwareAgent))
    collector.add((etl_script, PROV.actedOnBehalfOf, NS.OrkhanAbilov))
    collector.add((cube_script, FOAF.name, Literal("Cube Builder Script")))

    # Data Cube Valitation
    validator_script = NS.CubeValidatorScript
    collector.add((validator_script, RDF.type, PROV.SoftwareAgent))
    collector.add((validator_script, PROV.actedOnBehalfOf, NS.OrkhanAbilov))
    collector.add((validator_script, FOAF.name, Literal("Cube Validator Script", lang="en")))

    # author
    author = NS.OrkhanAbilov
    collector.add((author, RDF.type, PROV.Person))
    collector.add((author, RDF.type, PROV.Agent))
    collector.add((author, PROV.actedOnBehalfOf, NS.MFF_UK))
    collector.add((author, FOAF.givenName, Literal("Orkhan Abilov", lang="en")))
    collector.add((author, FOAF.mbox, URIRef("mailto:orkhanabilov17@gmail.com")))

    # MFF UK 
    organization = NS.MFF_UK
    collector.add((organization, RDF.type, PROV.Organization))
    collector.add((organization, RDF.type, PROV.Agent))
    collector.add((organization, FOAF.name, Literal("Matematicko-fyzikální fakulta, Univerzita Karlova", lang="cs")))
    collector.add((organization, FOAF.schoolHomepage, Literal("https://www.mff.cuni.cz/", datatype=XSD.anyURI)))

    # GitHub 
    github = NS.GitHub
    collector.add((github, RDF.type, PROV.Organization))
    collector.add((github, RDF.type, PROV.Agent))
    collector.add((github, FOAF.name, Literal("GitHub", lang="en")))
    collector.add((github, FOAF.homepage, Literal("https://github.com", datatype=XSD.anyURI)))

    # USGS 
    usgs = NS.USGS
    collector.add((usgs, RDF.type, PROV.Organization))
    collector.add((usgs, RDF.type, PROV.Agent))
    collector.add((usgs, FOAF.name, Literal("US Geological Survey", lang="en")))
    collector.add((usgs, FOAF.homepage, Literal("https://earthquake.usgs.gov", datatype=XSD.anyURI)))

    # Wikipedia
    wikipedia = NS.Wikipedia
    collector.add((wikipedia, RDF.type, PROV.Organization))
    collector.add((wikipedia, RDF.type, PROV.Agent))
    collector.add((wikipedia, FOAF.name, Literal("Wikipedia", lang="en")))
    collector.add((wikipedia, FOAF.homepage, Literal("https://en.wikipedia.org", datatype=XSD.anyURI)))


def create_activities(collector: Graph) -> None:
    # Apache Airflow 
    airflow_activity = NS.ApacheAirflowActivity
    collector.add((airflow_activity, RDF.type, PROV.Activity))
    collector.add((airflow_activity, PROV.startedAtTime, Literal("2025-04-21T08:00:00", datatype=XSD.dateTime)))
    collector.add((airflow_activity, PROV.endedAtTime, Literal("2025-04-21T08:15:00", datatype=XSD.dateTime)))
    collector.add((airflow_activity, PROV.used, NS.OlympicsData))
    collector.add((airflow_activity, PROV.used, NS.EarthquakeData))
    collector.add((airflow_activity, PROV.used, NS.CountriesPopData))
    collector.add((airflow_activity, PROV.wasAssociatedWith, NS.ApacheAirflow))

    # ETL Olympics data
    etl_olympics = NS.ETL_Olympics
    collector.add((etl_olympics, RDF.type, PROV.Activity))
    collector.add((etl_olympics, PROV.startedAtTime, Literal("2025-04-21T08:00:00", datatype=XSD.dateTime)))
    collector.add((etl_olympics, PROV.endedAtTime, Literal("2025-04-21T08:05:00", datatype=XSD.dateTime)))

    oly_use = BNode()
    collector.add((etl_olympics, PROV.qualifiedUsage, oly_use))
    collector.add((oly_use, RDF.type, PROV.Usage))
    collector.add((oly_use, PROV.entity, NS.OlympicsData))
    collector.add((oly_use, PROV.hadRole, Literal("source", datatype=XSD.string)))

    oly_assoc = BNode()
    collector.add((etl_olympics, PROV.qualifiedAssociation, oly_assoc))
    collector.add((oly_assoc, RDF.type, PROV.Association))
    collector.add((oly_assoc, PROV.agent, NS.ETLScript))
    collector.add((oly_assoc, PROV.agent, NS.ApacheAirflow))
    collector.add((oly_assoc, PROV.hadPlan, NS.DimCountries))

    # ETL Earthquake data
    etl_eq = NS.ETL_Earthquake
    collector.add((etl_eq, RDF.type, PROV.Activity))
    collector.add((etl_eq, PROV.startedAtTime, Literal("2025-04-21T08:05:00", datatype=XSD.dateTime)))
    collector.add((etl_eq, PROV.endedAtTime, Literal("2025-04-21T08:10:00", datatype=XSD.dateTime)))

    eq_use = BNode()
    collector.add((etl_eq, PROV.qualifiedUsage, eq_use))
    collector.add((eq_use, RDF.type, PROV.Usage))
    collector.add((eq_use, PROV.entity, NS.EarthquakeData))
    collector.add((eq_use, PROV.hadRole, Literal("source", datatype=XSD.string)))

    eq_assoc = BNode()
    collector.add((etl_eq, PROV.qualifiedAssociation, eq_assoc))
    collector.add((eq_assoc, RDF.type, PROV.Association))
    collector.add((eq_assoc, PROV.agent, NS.ETLScript))
    collector.add((eq_assoc, PROV.agent, NS.ApacheAirflow))

    # ETL Countries population data
    etl_countries = NS.ETL_Countries
    collector.add((etl_countries, RDF.type, PROV.Activity))
    collector.add((etl_countries, PROV.startedAtTime, Literal("2025-04-21T08:10:00", datatype=XSD.dateTime)))
    collector.add((etl_countries, PROV.endedAtTime, Literal("2025-04-21T08:15:00", datatype=XSD.dateTime)))

    # qualified usage for CountriesPopData
    countries_use = BNode()
    collector.add((etl_countries, PROV.qualifiedUsage, countries_use))
    collector.add((countries_use, RDF.type, PROV.Usage))
    collector.add((countries_use, PROV.entity, NS.CountriesPopData))
    collector.add((countries_use, PROV.hadRole, Literal("source", datatype=XSD.string)))

    # qualified association
    countries_assoc = BNode()
    collector.add((etl_countries, PROV.qualifiedAssociation, countries_assoc))
    collector.add((countries_assoc, RDF.type, PROV.Association))
    collector.add((countries_assoc, PROV.agent, NS.ETLScript))
    collector.add((countries_assoc, PROV.agent, NS.ApacheAirflow))
    collector.add((countries_assoc, PROV.hadPlan, NS.DimCountries))

    # Data Cube  
    cube_activity = NS.DataCubeActivity
    collector.add((cube_activity, RDF.type, PROV.Activity))
    collector.add((cube_activity, PROV.startedAtTime, Literal("2025-04-21T08:15:00", datatype=XSD.dateTime)))
    collector.add((cube_activity, PROV.endedAtTime, Literal("2025-04-21T08:20:00", datatype=XSD.dateTime)))

    # qualified usage for input datasets
    for source_entity, role in [
        (NS.FactOlympics, "fact table"),
        (NS.DimCountries, "dimension: country"),
        (NS.DimOlympicsSportEvent, "dimension: sport event")
    ]:
        use = BNode()
        collector.add((cube_activity, PROV.qualifiedUsage, use))
        collector.add((use, RDF.type, PROV.Usage))
        collector.add((use, PROV.entity, source_entity))
        collector.add((use, PROV.hadRole, Literal(role, datatype=XSD.string)))

    # qualified association
    cube_assoc = BNode()
    collector.add((cube_activity, PROV.qualifiedAssociation, cube_assoc))
    collector.add((cube_assoc, RDF.type, PROV.Association))
    collector.add((cube_assoc, PROV.agent, NS.CubeBuilderScript))
    collector.add((cube_assoc, PROV.agent, NS.ApacheAirflow))
    collector.add((cube_assoc, PROV.hadPlan, NS.DataCube))

    # Data Cube Validation
    cube_validation = NS.CubeValidationActivity
    collector.add((cube_validation, RDF.type, PROV.Activity))
    collector.add((cube_validation, PROV.startedAtTime, Literal("2025-04-21T08:20:00", datatype=XSD.dateTime)))
    collector.add((cube_validation, PROV.endedAtTime, Literal("2025-04-21T08:25:00", datatype=XSD.dateTime)))

    # usage of the DataCube
    validation_use = BNode()
    collector.add((cube_validation, PROV.qualifiedUsage, validation_use))
    collector.add((validation_use, RDF.type, PROV.Usage))
    collector.add((validation_use, PROV.entity, NS.DataCube))
    collector.add((validation_use, PROV.hadRole, Literal("validated input", datatype=XSD.string)))

    # association
    validation_assoc = BNode()
    collector.add((cube_validation, PROV.qualifiedAssociation, validation_assoc))
    collector.add((validation_assoc, RDF.type, PROV.Association))
    collector.add((validation_assoc, PROV.agent, NS.CubeValidatorScript))
    collector.add((validation_assoc, PROV.agent, NS.ApacheAirflow))
    collector.add((validation_assoc, PROV.hadPlan, NS.DataCube))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.error("Usage: python data_provenance.py output.trig")
        sys.exit(1)
    create_prov_data().serialize(format="trig", destination=sys.argv[1])
