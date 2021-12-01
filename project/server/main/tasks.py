# project/server/main/tasks.py

import os
from rq import get_current_job
import json


def coma_object_images(obj_id):
  job = get_current_job()
  directory = '/images/%s' %(obj_id)
 
  image_files = []
  # iterate over files in that directory
  for root, dirs, files in os.walk(directory):
    for filename in files:
      image_files.append(os.path.join(root, filename))

  response = json.dumps(image_files)
  return response

