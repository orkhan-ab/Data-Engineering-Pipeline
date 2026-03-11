#!/usr/bin/env python3

"""
Query 1:
    Retrieve all datasets with their titles, issued dates, and contact email.
    This helps to know which datasets exist and how to reach out about them.

Query 2:
    List all distributions with their media types and formats.
    This helps understand in which formats data is published and how it can be used.
"""

from rdflib import Graph
import sys

if len(sys.argv) != 2:
    print("Usage: python query.py output.ttl")
    sys.exit(1)


result = Graph()
result.parse(sys.argv[1], format="turtle")

# Query 1
query1 = """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX vcard: <https://www.w3.org/2006/vcard/ns#>

SELECT ?dataset ?title ?issued ?email
WHERE {
    ?dataset a dcat:Dataset ;
             dcterms:title ?title ;
             dcterms:issued ?issued ;
             dcat:contactPoint ?contact .
    ?contact vcard:hasEmail ?email .
}
"""

# Query 2
query2 = """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?distribution ?mediaType ?format
WHERE {
    ?distribution a dcat:Distribution ;
                  dcat:mediaType ?mediaType ;
                  dcterms:format ?format .
}
"""

print("Query 1: Datasets with Title, Issued Date, and Contact Email")
for row in result.query(query1):
    print(f"Dataset: {row.dataset}")
    print(f"Title: {row.title}")
    print(f"Issued: {row.issued}")
    print(f"Email: {row.email}")
    print("")

print("Query 2: Distributions with Media Type and Format")
for row in result.query(query2):
    print(f"Distribution: {row.distribution}")
    print(f"Media Type: {row.mediaType}")
    print(f"Format: {row.format}")
    print("")
