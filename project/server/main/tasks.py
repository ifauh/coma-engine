# project/server/main/tasks.py

import os
from rq import get_current_job
import json
import csv
from COMAJSONServer import COMAAPI

BUNDLE_PATH='/bundles'

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

def coma_object_images(obj_id):
  job = get_current_job()
  obj_id = TheBundle.IDFromName(obj_id)
  directory = '%s/%s' % (BUNDLE_PATH,obj_id)
 
  image_files = []
  # iterate over files in that directory
  for root, dirs, files in os.walk(directory):
    for filename in files:
      image_files.append(os.path.join(root, filename))

  response = json.dumps(image_files)
  return response

TheCOMAAPI = COMAAPI()

def coma_describe_fits(fits):
  return TheCOMAAPI.DescribeFits(fits)

