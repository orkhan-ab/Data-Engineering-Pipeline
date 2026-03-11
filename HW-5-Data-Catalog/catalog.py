#!/usr/bin/env python3

import logging
import sys
from rdflib import Graph, Literal, Namespace, URIRef, BNode
from rdflib.namespace import RDF, RDFS, XSD, DCAT, DCTERMS, FOAF, PROV

# Namespaces
NDBI = Namespace("https://ksi.mff.cuni.cz/~orkhan/232-NDBI046#")
EUROVOC = Namespace("http://publications.europa.eu/resource/dataset/eurovoc/")
FREQ = Namespace("https://publications.europa.eu/resource/distribution/frequency/rdf/skos_core/frequencies-skos.rdf#")
FILETYPES = Namespace("https://publications.europa.eu/resource/distribution/file-type/rdf/skos_core/filetypes-skos.rdf#")
COUNTRY = Namespace("https://publications.europa.eu/resource/distribution/country/rdf/skos_core/countries-skos.rdf#")
VCARD = Namespace("https://www.w3.org/2006/vcard/ns#")


def create_catalog_description() -> Graph:
    result = Graph()
    result.bind("ndbi", NDBI)
    result.bind("dcat", DCAT)
    result.bind("dcterms", DCTERMS)
    result.bind("foaf", FOAF)
    result.bind("xsd", XSD)
    result.bind("prov", PROV)
    result.bind("freq", FREQ)
    result.bind("filet", FILETYPES)
    result.bind("country", COUNTRY)
    result.bind("eurovoc", EUROVOC)
    result.bind("vcard", VCARD)

    create_catalog(result)
    create_publisher(result)
    create_creator(result)
    create_dataset(result)
    create_distributions(result)

    return result


def create_catalog(collector: Graph) -> None:
    catalog = NDBI.Catalog
    collector.add((catalog, RDF.type, DCAT.Catalog))
    collector.add((catalog, DCAT.dataset, NDBI.OlympicsDataCube))
    # Provenance metadata
    collector.add((catalog, DCTERMS.publisher, NDBI.Publisher))
    collector.add((catalog, DCTERMS.issued, Literal("2025-04-30T00:00:00", datatype=XSD.dateTime)))
    collector.add((catalog, DCTERMS.modified, Literal("2025-04-30T00:00:00", datatype=XSD.dateTime)))
    collector.add((catalog, DCAT.contactPoint, URIRef("mailto:orkhanabilov17@gmail.com")))
    # Domain metadata
    collector.add((catalog, DCTERMS.title, Literal("Olympics Data Cube Catalog", lang="en")))
    collector.add((catalog, DCTERMS.description, Literal("Catalog of the Olympics data cube dataset.", lang="en")))
    collector.add((catalog, DCAT.keyword, Literal("Olympics", lang="en")))
    collector.add((catalog, DCAT.keyword, Literal("data cube", lang="en")))
    collector.add((catalog, DCAT.keyword, Literal("rdf", lang="en")))
    collector.add((catalog, DCAT.theme, EUROVOC["5274"]))
    collector.add((catalog, DCAT.theme, EUROVOC["6030"]))
    # Business metadata
    collector.add((catalog, DCTERMS.accrualPeriodicity, FREQ.ANNUAL))
    collector.add((catalog, DCTERMS.accessRights, Literal("public")))
    collector.add((catalog, DCTERMS.license, URIRef("https://creativecommons.org/licenses/by/4.0/")))


def create_publisher(collector: Graph) -> None:
    publisher = NDBI.Publisher
    collector.add((publisher, RDF.type, FOAF.Organization))
    collector.add((publisher, RDFS.label, Literal("Faculty of Mathematics and Physics, Charles University in Prague", lang="en")))
    collector.add((publisher, RDFS.label, Literal("Matematicko-fyzikální fakulta, Karlova univerzita", lang="cs")))
    collector.add((publisher, FOAF.homepage, Literal("https://www.mff.cuni.cz/", datatype=XSD.anyURI)))


def create_creator(collector: Graph) -> None:
    creator = NDBI.OrkhanAbilov
    collector.add((creator, RDF.type, FOAF.Person))
    collector.add((creator, FOAF.givenName, Literal("Orkhan Abilov", lang="en")))
    collector.add((creator, FOAF.mbox, URIRef("mailto:orkhanabilov17@gmail.com")))


def create_dataset(collector: Graph) -> None:
    ds = NDBI.OlympicsDataCube
    collector.add((ds, RDF.type, DCAT.Dataset))
    collector.add((ds, DCAT.distribution, NDBI.FactOlympicsCSV))
    collector.add((ds, DCAT.distribution, NDBI.OlympicsCubeTTL))
    # Provenance metadata
    collector.add((ds, DCTERMS.creator, NDBI.OrkhanAbilov))
    collector.add((ds, DCTERMS.publisher, NDBI.Publisher))
    collector.add((ds, DCTERMS.issued, Literal("2025-04-30T00:00:00", datatype=XSD.dateTime)))
    collector.add((ds, DCTERMS.modified, Literal("2025-04-30T00:00:00", datatype=XSD.dateTime)))
    collector.add((ds, PROV.wasGeneratedBy, NDBI.DataCubeActivity))
    # Contact point
    cp = BNode()
    collector.add((ds, DCAT.contactPoint, cp))
    collector.add((cp, VCARD.fn, Literal("Orkhan Abilov")))
    collector.add((cp, VCARD.hasEmail, URIRef("mailto:orkhanabilov17@gmail.com")))
    # Domain metadata
    collector.add((ds, DCTERMS.title, Literal("Olympics Data Cube", lang="en")))
    collector.add((ds, DCTERMS.description, Literal("A data cube built from Olympic fact table.", lang="en")))
    collector.add((ds, DCAT.keyword, Literal("Olympics", lang="en")))
    collector.add((ds, DCAT.keyword, Literal("medals", lang="en")))
    collector.add((ds, DCAT.keyword, Literal("countries", lang="en")))
    collector.add((ds, DCAT.theme, EUROVOC["1530"]))
    collector.add((ds, DCAT.theme, EUROVOC["3329"]))
    collector.add((ds, DCAT.theme, EUROVOC["2554"]))
    collector.add((ds, DCTERMS.spatial, COUNTRY.CZE))
    # Temporal coverage
    period = BNode()
    collector.add((ds, DCTERMS.temporal, period))
    collector.add((period, RDF.type, DCTERMS.PeriodOfTime))
    collector.add((period, DCAT.startDate, Literal("2021-07-27", datatype=XSD.date)))
    collector.add((period, DCAT.endDate, Literal("2021-07-27", datatype=XSD.date)))
    # Business metadata
    collector.add((ds, DCTERMS.accessRights, Literal("public")))
    collector.add((ds, DCTERMS.rights, Literal("© Orkhan Abilov 2025")))
    collector.add((ds, DCTERMS.license, URIRef("https://creativecommons.org/licenses/by/4.0/")))


def create_distributions(collector: Graph) -> None:
    # Original CSV fact table
    d1 = NDBI.FactOlympicsCSV
    collector.add((d1, RDF.type, DCAT.Distribution))
    collector.add((d1, DCAT.accessURL, URIRef("https://gitlab.mff.cuni.cz/teaching/ndbi046/2024-25/orkhan-abilov/HW-3-Data-Cube/fact_olympics_raw.csv")))
    collector.add((d1, DCAT.downloadURL, URIRef("https://gitlab.mff.cuni.cz/teaching/ndbi046/2024-25/orkhan-abilov/HW-3-Data-Cube/fact_olympics_raw.csv")))
    collector.add((d1, DCAT.mediaType, URIRef("https://www.iana.org/assignments/media-types/text/csv")))
    collector.add((d1, DCAT.byteSize, Literal("144143", datatype=XSD.nonNegativeInteger)))
    collector.add((d1, DCTERMS.format, Literal("CSV", lang="en")))
    collector.add((d1, DCTERMS.title, Literal("CSV Distribution of Olympics Data", lang="en")))
    collector.add((d1, PROV.wasGeneratedBy, NDBI.ETL_Olympics))

    # RDF turtle data cube
    d2 = NDBI.OlympicsCubeTTL
    collector.add((d2, RDF.type, DCAT.Distribution))
    collector.add((d2, DCAT.accessURL, URIRef("https://gitlab.mff.cuni.cz/teaching/ndbi046/2024-25/orkhan-abilov/HW-3-Data-Cube/output.ttl")))
    collector.add((d2, DCAT.downloadURL, URIRef("https://gitlab.mff.cuni.cz/teaching/ndbi046/2024-25/orkhan-abilov/HW-3-Data-Cube/output.ttl")))
    collector.add((d2, DCAT.mediaType, URIRef("https://www.iana.org/assignments/media-types/text/turtle")))
    collector.add((d2, DCAT.byteSize, Literal("789012", datatype=XSD.nonNegativeInteger)))
    collector.add((d2, DCTERMS.format, Literal("Turtle", lang="en")))
    collector.add((d2, DCTERMS.title, Literal("TTL Distribution of Olympics Data", lang="en")))
    collector.add((d2, PROV.wasGeneratedBy, NDBI.DataCubeActivity))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.error("Usage: python catalog.py <output_file_path>")
        sys.exit(1)
    catalog = create_catalog_description()
    catalog.serialize(format="turtle", destination=sys.argv[1])
