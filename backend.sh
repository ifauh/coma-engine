#!/bin/bash

nohup /COMA/Coma/bin/coma-json-server -web-server -web-host 172.17.0.1 -web-port 5054 >COMAAPI.log 2>&1 &
