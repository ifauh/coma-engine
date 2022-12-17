# project/server/main/tasks.py

import os
import logging
from rq import get_current_job
import json
import csv
import re
from COMAJSONServer import COMAAPI
from COMADatabase import COMADB
from COMAPDS4 import Bundle, Collection

logging.basicConfig(filename='/usr/src/app/logs/coma.log', filemode='w', encoding='utf-8', level=logging.DEBUG)

TheBundle = Bundle()
TheCollection = Collection()

#def coma_object_images(obj_id):
#  job = get_current_job()
#  obj_id = TheBundle.IDFromName(obj_id)
#  directory = '%s/%s' % (BUNDLE_PATH,obj_id)
# 
#  image_files = []
#  # iterate over files in that directory
#  for root, dirs, files in os.walk(directory):
#    for filename in files:
#      image_files.append("/COMA" + os.path.join(root, filename))
#
#  response = json.dumps(image_files)
#  return response
# Need to call TheCOMADB.Run(query) then get results when they are available

TheCOMADB = COMADB()

def fits_download_url(fitsfile):
  base_url = "https://coma.ifa.hawaii.edu:/coma/"
  base_path = "/www/"
  path_part = fitsfile.split('/')
  base_dir = '/'.join(path_part[3:-1])
  base_path = '/'.join(path_part[3:])
  url = base_url + base_path + '.fits'
  cmd = "mkdir -p /www/%s; ln -s %s /www/%s.fits" %(base_dir, fitsfile, base_path)
  logging.debug(cmd)
  os.system(cmd)
  return url

def coma_object_images(obj_id):
  job = get_current_job()

  #add this back later when object ids are normalized
  #obj_id = TheBundle.IDFromName(obj_id)
  obj_id = obj_id.replace("<","").replace(">","")

  query = "select CONCAT(CONCAT(filepath, '/'), filename) as imagefile from coma.images where imagetype = 'OBJECT' and object = '%s';" % (obj_id)
  TheCOMADB.Run(query)

  image_files = []
  # serialize results into JSON
  row_headers=TheCOMADB.GetResultHeaders()
  row_values = TheCOMADB.GetResults()
  for row in row_values:
    url = fits_download_url(row[0])
    image_files.append(url)
    #image_files.append(dict(zip(row_headers,row)))

  response = json.dumps(image_files)
  return response

TheCOMAAPI = COMAAPI()

def coma_fits_header(fits):
  job = get_current_job()
  TheCOMAAPI.SetUUID(job.id)
  return TheCOMAAPI.HeaderFITS(fits)

def coma_fits_describe(fits):
  job = get_current_job()
  TheCOMAAPI.SetUUID(job.id)
  return TheCOMAAPI.DescribeFITS(fits)

def coma_fits_photometry(fits, objid, method, aperture):
  job = get_current_job()
  TheCOMAAPI.SetUUID(job.id)
  return TheCOMAAPI.CalibrateFITSPhotometry(fits, objid, method, aperture)

def coma_fits_calibrate(fits):
  job = get_current_job()
  TheCOMAAPI.SetUUID(job.id)
  return TheCOMAAPI.CalibrateFITS(fits)

def coma_insert_telescope(telescopeName):
  job = get_current_job()
  return TheCOMADB.InsertTelescope(telescopeName)

def query_results(query):
  TheCOMADB.Run(query)

  ret = {}
  # serialize results into JSON
  row_headers=TheCOMADB.GetResultHeaders()
  row_values = TheCOMADB.GetResults()
  for row in row_values:
    ret = row
    break;

  response = json.dumps(ret)
  return response

def coma_get_telescope(tel_id):
  job = get_current_job()
  #obj_id = TheBundle.IDFromName(tel_id)
  key = tel_id.replace("<","").replace(">","")

  query = "select * from coma.telescopes where telescopeid = '%s';" % (key)
  return query_results(query)

def coma_get_observatory(obs_id):
  job = get_current_job()

  #add this back later when object ids are normalized
  #obj_id = TheBundle.IDFromName(obj_id)
  obs_id = obs_id.replace("<","").replace(">","")

  query = "select * from coma.obscode where code = '%s';" % (obs_id)
  return query_results(query)
