#!/bin/bash
IFS=','

[ -z "$1" ] && echo "You must provide a manifest file argument" && exit 1
manifest="$1"

if [ ! -f "$manifest" ]
then
  echo "manifest file "${manifest}" must exist"
  exit 1
fi

cat "${manifest}" | while read -a arg
do
  id="${arg[0]}"
  object="${arg[1]}"
  fits="${arg[2]}"
  echo Ingesting $fits
  python3 ingest.py "$fits" "$object" --id "$id"
done
