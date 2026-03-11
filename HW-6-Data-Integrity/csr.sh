#!/bin/bash

openssl genrsa \
  -aes256 \
  -out private.key \
  2048

openssl req \
  -key private.key \
  -new \
  -out request.csr \
  -subj "/C=CZ/O='Charles University'/CN=ksi.mff.cuni.cz"

#openssl x509 \
#  -req \
#  -CA ca_root_certificate.crt \
#  -CAkey ca_private.key \
#  -in request.csr \
#  -out certificate.crt \
#  -days 365 \
#  -CAcreateserial

#openssl req -x509 \
#  -newkey rsa:4096 \
#  -sha256 \
#  -nodes \
#  -keyout private.key \
#  -out certificate.crt \
#  -subj "/C=CZ/O='Charles University'/CN=ksi.mff.cuni.cz"