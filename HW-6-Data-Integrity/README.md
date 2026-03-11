# Data Integrity

## Description of Files

### `catalog_with_checksum.py`
This script generates the `data-catalog.ttl` file, which describes my dataset and its distributions using the DCAT vocabulary. I extended it to also calculate SHA1 checksums for both the CSV and TTL files and include them using the `spdx:checksum`.

**Inputs:**
- The CSV file from my HW3 (`fact_olympics_raw.csv`)
- The TTL file from my HW3 (`output.ttl`)

**Output:**
- `data-catalog.ttl` – the catalog RDF file with metadata and checksums

### `csr.sh`
I used git bash for running (csr.sh). This shell script creates a private key and a certificate signing request (CSR) using OpenSSL. I sent the `.csr` to get it signed.

**Output:**
- `private.key` – my private key (not published)
- `request.csr` – my certificate signing request

### `sign_cat.sh`
I used git bash for running (sign_cat.sh). This script signs the catalog file using the private key and creates a digital signature. I used this to prove that the catalog file was not changed.

**Input:**
- `data-catalog.ttl`

**Outputs:**
- `data-catalog.sha256` – the raw SHA256 signature
- `data-catalog.sha256.sign` – the signature encoded in Base64 (used for publishing)

## Data Files

- `fact_olympics_raw.csv` – the original CSV fact table used for the data cube
- `output.ttl` – the RDF Turtle version of my data cube
- `certificate.crt` – the certificate I received
- `data-catalog.ttl` – the final catalog with checksums
- `data-catalog.sha256.sign` – the digital signature of the catalog


