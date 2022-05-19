# COMAJSONServer.py

# encapsulate Jan Kleyna's COMA JSON API for Python

import os
import json
import mariadb
import logging

class COMADB:
  # default constructor

  def __init__(self):
    self.debug=False
    self.config = {
      'host': os.getenv('COMA_DB_HOST', default="172.17.0.1"),
      'port': int(os.getenv('COMA_DB_PORT', default="0")),
      'user': os.getenv('COMA_DB_USER', default="nobody"),
      'password': os.getenv('COMA_DB_PASS', default=""),
      'database': os.getenv('COMA_DB_NAME', default="coma"),
      'autocommit': True,
    }
    if self.config["port"] > 0:
      logging.basicConfig(filename='/usr/src/app/logs/coma.log', filemode='a', encoding='utf-8', level=logging.DEBUG)
      self.OpenDB()


  def __del__(self):
    self.CloseDB()

  def OpenDB(self, port=0):
    # connection for MariaDB
    #print(self.config)
    logging.debug("OpenDB: " + str(self.config))
    self.conn = mariadb.connect(**self.config)
    #print(self.conn)
    #self.conn = None

  def CloseDB(self):
    self.conn = None

  def Run(self, dmlSQL, dmlData):
    # create a connection cursor
    self.cursor = self.conn.cursor()
    # execute a SQL statement
    # TODO check for sql injection
    logging.debug(queryStr)
    return self.cursor.execute(dmlSQL, dmlData)
 
  def GetResultHeaders(self):
    # serialize results into JSON
    self.column_headers=[x[0] for x in self.cursor.description]
    return self.column_headers
 
  def GetResults(self):
    # fetch all rows and return as list of dicts
    rv = self.cursor.fetchall()
    self.column_values = []
    # strip unwanted characters from results
    for results in rv:
      row = []
      for r in results:
        row.append(r.replace('\r',""))
      self.column_values.append(row)
      #self.column_values.append(dict(zip(self.column_headers,result)))
    return self.column_values
 
  def InsertRow(self, insertStr, values):
    logging.debug(insertStr)
    try:
      # create a connection cursor
      self.cursor = self.conn.cursor()
      ret = self.cursor.execute(insertStr, values)
      #self.cursor.commit()
    except mariadb.Error as e:
      logging.debug(f"Error adding entry to database: {e}")
      ret = ""
    return ret

  def InsertTelescope(self, telescopeName):
    # create a connection cursor
    values = (1, telescopeName)
    insert = "INSERT INTO telescopes (telescopeid, telescopename) VALUES (?, ?)"
    return self.InsertRow(insert, values)

  def InsertInstrument(self, instrumentName):
    # create a connection cursor
    values = (int(1), instrumentName)
    insert = "INSERT INTO tinstruments (tinstuumentid, tinstrumentname) VALUES (?, ?)"
    return self.InsertRow(insert, values)

