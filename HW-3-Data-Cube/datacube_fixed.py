#!/usr/bin/env python3
import pandas as pd
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, SKOS, XSD, QB, DCTERMS

BASE = "http://example.org/olympics/"
EX = Namespace(BASE + "ontology#")
EXR = Namespace(BASE + "resources/")
SDMX_M = Namespace("http://purl.org/linked-data/sdmx/2009/measure#")
SDMX_D = Namespace("http://purl.org/linked-data/sdmx/2009/dimension#")

def create_concept_scheme(collector, scheme_uri, label):
    collector.add((scheme_uri, RDF.type, SKOS.ConceptScheme))
    collector.add((scheme_uri, SKOS.prefLabel, Literal(label, lang="en")))

def create_concepts(collector, df, column, scheme_uri, concept_prefix):
    for value in df[column].dropna().unique():
        uri = EXR[f"{concept_prefix}/{value.replace(' ', '_')}"]
        collector.add((uri, RDF.type, SKOS.Concept))
        collector.add((uri, SKOS.prefLabel, Literal(value, lang="en")))
        collector.add((uri, SKOS.inScheme, scheme_uri))

def define_sdmx_metadata(collector):
    for prop, label in [
        (SDMX_D.refArea, "Reference Area"),
        (SDMX_D.refPeriod, "Reference Period"),
        (SDMX_D.activity, "Activity"),
        (SDMX_M.obsValue, "Observation Value"),
    ]:
        collector.add((prop, RDF.type, RDF.Property))
        collector.add((prop, RDFS.label, Literal(label, lang="en")))

def define_dimensions(collector):
    dims = []

    d = EX.country
    collector.add((d, RDF.type, QB.DimensionProperty))
    collector.add((d, SKOS.prefLabel, Literal("Country", lang="en")))
    collector.add((d, RDFS.subPropertyOf, SDMX_D.refArea))
    collector.add((d, RDFS.range, SKOS.Concept))
    collector.add((d, QB.codeList, EX.countryScheme))
    dims.append(d)

    s = EX.sport
    collector.add((s, RDF.type, QB.DimensionProperty))
    collector.add((s, SKOS.prefLabel, Literal("Sport", lang="en")))
    collector.add((s, RDFS.subPropertyOf, SDMX_D.activity))
    collector.add((s, RDFS.range, SKOS.Concept))
    collector.add((s, QB.codeList, EX.sportScheme))
    dims.append(s)

    y = EX.year
    collector.add((y, RDF.type, QB.DimensionProperty))
    collector.add((y, SKOS.prefLabel, Literal("Year", lang="en")))
    collector.add((y, RDFS.subPropertyOf, SDMX_D.refPeriod))
    collector.add((y, RDFS.range, XSD.gYear))
    dims.append(y)

    return dims

def define_measure(collector):
    m = EX.medalCount
    collector.add((m, RDF.type, QB.MeasureProperty))
    collector.add((m, SKOS.prefLabel, Literal("Medal Count", lang="en")))
    collector.add((m, RDFS.subPropertyOf, SDMX_M.obsValue))
    return [m]

def define_structure(collector, dims, measures):
    dsd = EX.structure
    collector.add((dsd, RDF.type, QB.DataStructureDefinition))
    for i, d in enumerate(dims, 1):
        c = BNode()
        collector.add((dsd, QB.component, c))
        collector.add((c, QB.dimension, d))
        collector.add((c, QB.order, Literal(i, datatype=XSD.integer)))
    for m in measures:
        c = BNode()
        collector.add((dsd, QB.component, c))
        collector.add((c, QB.measure, m))

    slice_key = EX.sliceKey_country
    collector.add((slice_key, RDF.type, QB.SliceKey))
    collector.add((slice_key, QB.componentProperty, EX.country))
    collector.add((dsd, QB.sliceKey, slice_key))

    return dsd

def create_dataset(collector, dsd):
    ds = EXR.dataset
    collector.add((ds, RDF.type, QB.DataSet))
    collector.add((ds, QB.structure, dsd))
    collector.add((ds, DCTERMS.publisher, Literal("Student 10824430")))
    collector.add((ds, DCTERMS.title, Literal("Olympics Medals Cube", lang="en")))
    collector.add((ds, DCTERMS.issued, Literal("2025-04-17", datatype=XSD.date)))
    return ds

def create_observations(collector, ds, df):
    for i, row in df.iterrows():
        o = EXR[f"observation/{i}"]
        collector.add((o, RDF.type, QB.Observation))
        collector.add((o, QB.dataSet, ds))
        collector.add((o, EX.country, EXR[f"country/{row.country.replace(' ', '_')}"]))
        collector.add((o, EX.sport, EXR[f"sport/{row.sport.replace(' ', '_')}"]))
        collector.add((o, EX.year, Literal(row.year, datatype=XSD.gYear)))
        collector.add((o, EX.medalCount, Literal(1, datatype=XSD.integer)))

def create_slice(collector, ds, dsd, df, country_name):
    country_uri = EXR[f"country/{country_name.replace(' ', '_')}"]
    sl = EXR[f"slice/{country_name.replace(' ', '_')}"]
    collector.add((sl, RDF.type, QB.Slice))
    collector.add((sl, QB.sliceStructure, EX.sliceKey_country))
    collector.add((sl, QB.dataSet, ds))
    collector.add((sl, EX.country, country_uri))
    for i, row in df[df['country'] == country_name].iterrows():
        collector.add((sl, QB.observation, EXR[f"observation/{i}"]))

def main():
    df = pd.read_csv("fact_olympics_raw.csv")

    result = Graph()
    result.bind("ex", EX)
    result.bind("exr", EXR)
    result.bind("qb", QB)
    result.bind("skos", SKOS)
    result.bind("dcterms", DCTERMS)
    result.bind("sdmx-m", SDMX_M)
    result.bind("sdmx-d", SDMX_D)

    define_sdmx_metadata(result)  

    create_concept_scheme(result, EX.countryScheme, "Countries")
    create_concepts(result, df, "country", EX.countryScheme, "country")
    create_concept_scheme(result, EX.sportScheme, "Sports")
    create_concepts(result, df, "sport", EX.sportScheme, "sport")

    dims = define_dimensions(result)
    measures = define_measure(result)
    dsd = define_structure(result, dims, measures)
    ds = create_dataset(result, dsd)

    create_observations(result, ds, df)
    create_slice(result, ds, dsd, df, country_name="United States")

    result.serialize(destination="olympics_cube.ttl", format="turtle")
    print("olympics_cube.ttl written.")

if __name__ == "__main__":
    main()
