# project/server/main/tasks.py

import os
import logging
from rq import get_current_job
import json
import csv
from COMAJSONServer import COMAAPI
from COMADatabase import COMADB

BUNDLE_PATH='/bundles'
logging.basicConfig(filename='/usr/src/app/logs/coma.log', filemode='w', encoding='utf-8', level=logging.DEBUG)

def has_digits(inStr):
  return any(char.isdigit() for char in inStr)

def list_to_string(inList):
  return ''.join([str(item) for item in inList])

class Bundle:
  # default constructor
  def __init__(self):
    self.debug=False
    self.Load()
    self.Dump()
 
  # a method for loading bundle names and ids
  def Load(self):
    self.bundle={}

    cometLIDFile = BUNDLE_PATH + '/etc' + '/bundle-lid-comet.tsv'
    with open(cometLIDFile) as fd:
      firstRow=1
      rd = csv.reader(fd, delimiter="\t", quotechar='"')
      for row in rd:
        if(firstRow):
          firstRow = 0
          continue

        lid=row[0].strip()
        if(self.debug):
          print("LID: %s" % lid)
  
        title=row[1]
        if(self.debug):
          print("TITLE: %s" % title)
  
        # parse and load the main ids
        titles=title.split('(')
        for title in titles:
          #title=list_to_string(titles[ind])
          title=title.split(')')
          title=list_to_string(title[0])
          title=title.strip()
          if(self.debug):
            print("TITLE: %s" % title)

          self.bundle[title] = lid

        # parse and load alternate ids
        aliases = row[2].split(',')
        if(self.debug):
          print("  %s" % aliases)
        if aliases[0] != "":
          for alias in aliases:
            if(self.debug):
              print("  %s" % alias)

            alias = alias.strip()
            self.bundle[alias] = lid

  def Dump(self):
    with open("/bundles/etc/bundle-lids.csv", "w") as outfile:
      for key in self.bundle:
        bundle_lid = "%s,%s\n" % (key, self.bundle[key])
        outfile.write(bundle_lid)

  def IDFromName(self, name):
    #try with object
    #if object has no digits in it then append 1 and try again
    #if no match then raise exception for now return "UNKNOWN"
    matched="UNKNOWN"
    if name in self.bundle:
      matched=self.bundle[name]
    elif name.lower() in self.bundle:
      matched=self.bundle[name.lower()]
    elif name.upper() in self.bundle:
      matched=self.bundle[name.upper()]
    return matched

TheBundle = Bundle()

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
  return TheCOMAAPI.DescribeFITS(fits)

def coma_fits_photometry(fits, objid, method, aperture):
  job = get_current_job()
  TheCOMAAPI.SetUUID(job.id)
  return TheCOMAAPI.CalibrateFITSPhotometry(fits, objid, method, aperture)

def coma_fits_calibrate(fits):
  job = get_current_job()
  TheCOMAAPI.SetUUID(job.id)
  return TheCOMAAPI.CalibrateFITS(fits)

