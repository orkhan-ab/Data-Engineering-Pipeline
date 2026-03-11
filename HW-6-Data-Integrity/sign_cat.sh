#!/bin/bash

openssl dgst \
  -sha256 \
  -sign private.key \
  -out data-catalog.sha256 \
  data-catalog.ttl

openssl base64 \
  -in data-catalog.sha256 \
  -out data-catalog.sha256.sign