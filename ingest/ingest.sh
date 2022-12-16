#!/bin/bash
IFS=','
cat manifest | while read -a arg
do
  id="${arg[0]}"
  object="${arg[1]}"
  fits="${arg[2]}"
  echo Ingesting $fits
  python3 ingest.py "$fits" "$object" --id "$id"
done
