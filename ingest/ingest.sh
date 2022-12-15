#!/bin/bash

cat manifest | while read fits
do
  echo Ingesting $fits
  python3 ingest.py $fits 'C/2017 K2'
done
