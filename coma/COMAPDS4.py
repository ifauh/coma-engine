import os
import logging
import json
import csv
import re

#logging.basicConfig(filename='coma.log', filemode='w', encoding='utf-8', level=logging.DEBUG)

def has_digits(inStr):
  return any(char.isdigit() for char in inStr)

def list_to_string(inList):
  return ''.join([str(item) for item in inList])

class Bundle:
  # default constructor
  def __init__(self, root_path='/', path='bundle/etc', file_name='bundle-lid-comet.tsv'):
    self.debug=False
    self.path = '{0}/{1}/{2}'.format(root_path, path, file_name)
    self.Load()
    self.Dump()
 
  # a method for loading bundle names and ids
  def Load(self):
    self.bundle={}

    with open(self.path) as fd:
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
    with open("./bundle-lids.csv", "w") as outfile:
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


class Collection:
  # default constructor
  def __init__(self, root_path='/', path='collection/etc', file_name='collection-lid.tsv'):
    self.debug=False
    self.path = '{0}/{1}/{2}'.format(root_path, path, file_name)
    self.Load()
    self.Dump()
 
  # a method for loading collection names and ids
  def Load(self):
    self.collection={}
    self.instrument={}
    self.telescope={}

    with open(self.path) as file:
       
      # read tab-delimited file
      tsv_file = csv.reader(file, delimiter="\t")
      next(tsv_file)
     
      # parse each line into lid, telinst, tel, inst
      for line in tsv_file:
        lid=line[0]
        if(self.debug):
          logging.debug("LID: {0}".format(lid))
  
        telinst=line[1]
        if(self.debug):
          logging.debug("TELINST: {0}".format(telinst))

        tel=line[2]
        if(self.debug):
          logging.debug("TELESCOPE: {0}".format(tel))

        inst=line[3]
        if(self.debug):
          logging.debug("INSTRUMENT: {0}".format(inst))

        self.collection[telinst] = lid
        self.instrument[telinst] = inst
        self.telescope[telinst] = tel


  def Dump(self):
    with open("./collection-lids.csv", "w") as outfile:
      for key in self.collection:
        collection_lid = "%s,%s,%s,%s\n" % (key, self.collection[key], self.telescope[key], self.instrument[key])
        outfile.write(collection_lid)

  def IDFromName(self, name):
    #try with object
    #if object has no digits in it then append 1 and try again
    #if no match then raise exception for now return "UNKNOWN"
    matched="UNKNOWN"
    if name in self.collection:
      matched=self.collection[name]
    elif name.lower() in self.collection:
      matched=self.collection[name.lower()]
    elif name.upper() in self.collection:
      matched=self.collection[name.upper()]
    return matched


# Defining main function
def main():
  logging.basicConfig(filename='coma.log', filemode='w', level=logging.DEBUG)
  bundle = Bundle(root_path='/COMA')
  bundle.Dump()
  collect = Collection(root_path='/COMA')
  collect.Dump()
  
  
# Using the special variable 
# __name__
if __name__=="__main__":
    main()
