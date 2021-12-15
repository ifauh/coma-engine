# project/server/main/views.py

import redis
from rq import Queue, Connection
from flask import render_template, Blueprint, jsonify, request, current_app
from flask_cors import CORS

import json

from project.server.main.tasks import coma_object_images, coma_describe_fits, coma_fits_photometry

def job_tasks(job):
  job_def = json.loads(job)
  # enumerate the array of tasks
  #for task in job_def:
  
  #with Connection(redis.from_url(current_app.config["REDIS_URL"])):
  #  q = Queue()
  #  task = q.enqueue(coma_describe_fits, fits_file)
  #response_object = {
  #  "status": "success",
  #  "task": { "id": task.get_id() },
  #}
  return job_def

main_blueprint = Blueprint("main", __name__,)
CORS(main_blueprint)

# Configure for Cross-Origin Resource Sharing (CORS)
cors_config = {
  "origins": ["*"],
  "methods": ["OPTIONS", "GET", "POST"],
  "allow_headers": ["Authorization", "Content-Type"]
}
#CORS(app, resources={"/": cors_config})


@main_blueprint.route("/", methods=["GET"])
#@cross_origin(**api_cors_config)
def home():
  return render_template("main/home.html")


# API for list all URLs
@main_blueprint.route("/routes/", methods=["GET"])
#@cross_origin(**api_cors_config)
def list_routes():
  response_object = {
      "routes": {
        "url": "/routes/", 
        "method": "GET",
        "description": "List of REST API URLs",
      },
      "objects": {
        "url": "/objects/", 
        "method": "GET",
        "description": "List of valid object IDs",
      },
      "object-images": {
        "url": "/object/images/<id>/", 
        "method": "GET",
        "description": "List object images",
        "<id>": "Object ID",
      },
      "fits-header": {
        "url": "/fits/header/",
        "method": "POST",
        "description": "List FITS file header values for a fits file",
        "fits_file": "full path of FITS file",
      },
      "fits-photometry": {
        "url": "/fits/photometry/",
        "method": "POST",
        "description": "Run FITS image photometry",
        "fits_file": "full path of FITS file",
        "object": "COMA id of the object, e.g. 9P",
        "method": "COMA photometry method, e.g. TheAperturePhotometry",
        "aperture": "radius/aperture, scalar or vector",
      },
      "run-job": {
        "url": "/job/run/",
        "method": "POST",
        "description": "Launch a job comprising a set of tasks defined in a JSON string",
        "job": "JSON encoded string describing the tasks comprising the job",
      },
      "task-status": {
        "url": "/task/status/<task_id/",
        "method": "GET",
        "description": "Poll task status e.g. finished, failed",
        "<task_id>": "Task UUID",
      },
      "task-result": {
        "url": "/task/result/<task_id/",
        "method": "GET",
        "description": "Retrieve task output as a JSON enocded string",
        "<task_id>": "Task UUID",
      },
  }
  return jsonify(response_object)

# API for list object ids
@main_blueprint.route("/objects/", methods=["GET"])
#@cross_origin(**api_cors_config)
def list_objects():
  response_object = {
    "9p": "9P/1867 G1 (Tempel 1)",
  }
  return jsonify(response_object)


#@main_blueprint.route("/tasks", methods=["POST"])
#def run_task():
#  task_type = request.form["type"]
#  with Connection(redis.from_url(current_app.config["REDIS_URL"])):
#    q = Queue()
#    task = q.enqueue(create_task, task_type)
#  response_object = {
#    "status": "success",
#    "task": { "id": task.get_id() },
#  }
#  return jsonify(response_object), 202


@main_blueprint.route("/task/status/<task_id>/", methods=["GET"])
#@cross_origin(**api_cors_config)
def get_status(task_id):
  with Connection(redis.from_url(current_app.config["REDIS_URL"])):
    q = Queue()
    task = q.fetch_job(task_id)
  if task:
    response_object = {
      "status": "success",
      "task": {
        "id": task.get_id(),
        "status": task.get_status(),
      },
    }
  else:
    response_object = { "status": "error" }
  return jsonify(response_object)

@main_blueprint.route("/task/result/<task_id>/", methods=["GET"])
#@cross_origin(**api_cors_config)
def get_result(task_id):
  with Connection(redis.from_url(current_app.config["REDIS_URL"])):
    q = Queue()
    task = q.fetch_job(task_id)
  if task and task.result:
    response_object = {
      "status": "success",
      "task": {
        "id": task.get_id(),
        "status": task.get_status(),
        "enqueued": task.enqueued_at.isoformat(),
      },
      "data": task.result
    }
  else:
    response_object = { "status": "error" }
  return jsonify(response_object)

@main_blueprint.route("/object/images/<obj_id>", methods=["GET"])
#@cross_origin(**api_cors_config)
def task_object_images(obj_id):
  with Connection(redis.from_url(current_app.config["REDIS_URL"])):
    q = Queue()
    task = q.enqueue(coma_object_images, obj_id)
  response_object = {
    "status": "success",
    "task": { "id": task.get_id() },
  }
  return jsonify(response_object), 202

@main_blueprint.route("/fits/header/", methods=["POST"])
#@cross_origin(**api_cors_config)
def task_fits_header():
  fits_file = request.form["fits_file"]
  with Connection(redis.from_url(current_app.config["REDIS_URL"])):
    q = Queue()
    task = q.enqueue(coma_describe_fits, fits_file)
  response_object = {
    "status": "success",
    "task": { "id": task.get_id() },
  }
  return jsonify(response_object), 202

@main_blueprint.route("/fits/photometry/", methods=["POST"])
#@cross_origin(**api_cors_config)
def task_fits_photometry():
  fits_file = request.form["fits_file"]
  objid = request.form["object"]
  method = request.form["method"]
  aperture = request.form["aperture"]
  with Connection(redis.from_url(current_app.config["REDIS_URL"])):
    q = Queue()
    task = q.enqueue(coma_fits_photometry, fits_file, objid, method, aperture)
  response_object = {
    "status": "success",
    "task": { "id": task.get_id() },
  }
  return jsonify(response_object), 202

@main_blueprint.route("/job/run/", methods=["POST"])
#@cross_origin(**api_cors_config)
def task_run_job():
  job = request.form["job"]
  response_object = job_tasks(job)
  return jsonify(response_object), 202

#@main_blueprint.route("/tasks", methods=["POST"])
#def run_task():
#  with Connection(redis.from_url(current_app.config["REDIS_URL"])):
#    q = Queue()
#    task = q.enqueue(create_task, task_type)
#  response_object = {
#    "status": "success",
#    "task": { "id": task.get_id() },
#  }
#  return jsonify(response_object), 202


