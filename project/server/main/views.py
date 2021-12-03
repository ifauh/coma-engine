# project/server/main/views.py

import redis
from rq import Queue, Connection
from flask import render_template, Blueprint, jsonify, request, current_app

from project.server.main.tasks import coma_object_images, coma_describe_fits

main_blueprint = Blueprint("main", __name__,)


@main_blueprint.route("/", methods=["GET"])
def home():
  return render_template("main/home.html")


# API for list all URLs
@main_blueprint.route("/routes/", methods=["GET"])
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
  }
  return jsonify(response_object)

# API for list object ids
@main_blueprint.route("/objects/", methods=["GET"])
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


@main_blueprint.route("/tasks/<task_id>", methods=["GET"])
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

@main_blueprint.route("/result/<task_id>", methods=["GET"])
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


