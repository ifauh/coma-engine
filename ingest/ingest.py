import requests
import logging
import json
import csv
import time
from itertools import chain
from os.path import exists
import argparse

try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")

parser = argparse.ArgumentParser()
parser.add_argument("fits", help="FITS file to ingest")
parser.add_argument("object", help="central object in FITS file")
parser.add_argument("-m", "--method", default='TheAperturePhotometry', help="aperture photometry method to use")
parser.add_argument("-a", "--aperture", default='[5,10]', help="aperture list, e.g. [5,10]")
parser.add_argument("-v", "--verbosity", action="count", default=0)
args = parser.parse_args()

if args.verbosity > 0:
  requests_log.propagate = True
  if args.verbosity > 4:
    requests_log.setLevel(logging.DEBUG)
  elif args.verbosity > 3:
    requests_log.setLevel(logging.INFO)
  elif args.verbosity > 2:
    requests_log.setLevel(logging.WARN)
  elif args.verbosity > 1:
    requests_log.setLevel(logging.INFO)
  else:
    requests_log.setLevel(logging.CRITICAL)
else:
  requests_log.propagate = False
  requests_log.setLevel(logging.NOTSET)

IMGFILE='description.csv'
img_header = False
if exists(IMGFILE):
  img_file = open(IMGFILE, 'a')
else:
  img_file = open(IMGFILE, 'w')
  img_header = True

# create the csv writer object
img_writer = csv.writer(img_file)

CALFILE='calibration.csv'
cal_header = False
if exists(CALFILE):
  cal_file = open(CALFILE, 'a')
else:
  cal_file = open(CALFILE, 'w')
  cal_header = True

# create the csv writer object
cal_writer = csv.writer(cal_file)
 
PHOTFILE='photometry.csv'
phot_header = False
if exists(PHOTFILE):
  phot_file = open(PHOTFILE, 'a')
else:
  phot_file = open(PHOTFILE, 'w')
  phot_header = True

# create the csv writer object
phot_writer = csv.writer(phot_file)
 

##################################################

FITS=args.fits
OBJECT=args.object
ARGS={
  'fits_file': FITS
}

################
# First describe FITS file
API='https://coma.ifa.hawaii.edu/api/fits/describe'
response = [requests.post(API, data=ARGS, verify=False)]
cursor=0
print("Status code: ", response[cursor].status_code)
if response[cursor].status_code <= 202:
  data = response[cursor].json()
  if data['status'] == 'success':
    guid = data['task']['id']

data = {}
while cursor < 10 and 'data' not in data:
  API='https://coma.ifa.hawaii.edu/api/task/result/%s' %(guid)
  response.append(requests.get(API, verify=False))
  cursor+=1
  print("Status code: ", response[cursor].status_code)
  if response[cursor].status_code <= 202:
    data = response[cursor].json()
    if 'data' not in data:
      time.sleep(1)

description = json.loads(data['data'])
print(description)

del description['TYPE']

# Counter variable used for writing
# headers to the CSV file
if img_header:
  header = description.keys()
  img_writer.writerow(header)
  img_header = False

img_writer.writerow(description.values())

################
# Next calibrate FITS file
API='https://coma.ifa.hawaii.edu/api/fits/calibrate'
response = [requests.post(API, data=ARGS, verify=False)]
cursor=0
print("Status code: ", response[cursor].status_code)
if response[cursor].status_code <= 202:
  data = response[cursor].json()
  if data['status'] == 'success':
    guid = data['task']['id']

data = {}
while cursor < 20 and 'data' not in data:
  API='https://coma.ifa.hawaii.edu/api/task/result/%s' %(guid)
  response.append(requests.get(API, verify=False))
  cursor+=1
  print("Status code: ", response[cursor].status_code)
  if response[cursor].status_code <= 202:
    data = response[cursor].json()
    if 'data' not in data:
      time.sleep(1)

calibration = json.loads(data['data'])
print(calibration)
qualities = calibration['QUALITIES-INFO']
wcs = calibration['WCS-INFO']
wcscal = wcs['WCS']
del wcs['WCS']
photcalib = calibration['PHOT-CALIB-INFO']

#del calibration['TYPE']

header = []
row = []
for key, val in qualities.items():
  header.append(key)
  row.append(val)
for key, val in wcs.items():
  header.append(key)
  row.append(val)
for key, val in wcscal.items():
  header.append(key)
  row.append(val)
for key, val in photcalib.items():
  header.append(key)
  row.append(val)
if cal_header:
  cal_writer.writerow(header)
  cal_header = False
cal_writer.writerow(row)

################
# Next do photometry on FITS file
API='https://coma.ifa.hawaii.edu/api/fits/photometry'
ARGS['method'] = args.method
ARGS['aperture'] = args.aperture
ARGS['object'] = OBJECT
response = [requests.post(API, data=ARGS, verify=False)]
cursor=0
print("Status code: ", response[cursor].status_code)
if response[cursor].status_code <= 202:
  data = response[cursor].json()
  if data['status'] == 'success':
    guid = data['task']['id']

data = {}
while cursor < 30 and 'data' not in data:
  API='https://coma.ifa.hawaii.edu/api/task/result/%s' %(guid)
  response.append(requests.get(API, verify=False))
  cursor+=1
  print("Status code: ", response[cursor].status_code)
  if response[cursor].status_code <= 202:
    data = response[cursor].json()
    if 'data' not in data:
      time.sleep(1)

photometry = json.loads(data['data'])
print(photometry)

photval = photometry['PHOTOMETRY-RESULTS'][0]
del photometry['PHOTOMETRY-RESULTS']
del photometry['TYPE']

del photval['TYPE']
photmeta = {}
photmeta['ID'] = photval['ID']
del photval['ID']
photmeta['XPIX-FINAL'] = photval['XPIX-FINAL']
del photval['XPIX-FINAL']
photmeta['YPIX-FINAL'] = photval['YPIX-FINAL']
del photval['YPIX-FINAL']
photmeta['RA-FINAL'] = photval['RA-FINAL']
del photval['RA-FINAL']
photmeta['DEC-FINAL'] = photval['DEC-FINAL']
del photval['DEC-FINAL']
photmeta['POSITION-WAS-TUNED'] = photval['POSITION-WAS-TUNED']
del photval['POSITION-WAS-TUNED']

for aperture in range(2):
  header = []
  row = []
  for key, val in photometry.items():
    header.append(key)
    row.append(val)
  for key, val in photmeta.items():
    header.append(key)
    row.append(val)
  for key, val in photval.items():
    header.append(key)
    row.append(val[aperture])
  # headers to the CSV file
  if phot_header:
    phot_writer.writerow(header)
    phot_header = False
  phot_writer.writerow(row)

###############################################

img_file.close()
cal_file.close()
phot_file.close()
