# project/server/main/views.py

import redis
from rq import Queue, Connection
from flask import render_template, Blueprint, jsonify, request, current_app

from project.server.main.tasks import coma_object_images

main_blueprint = Blueprint("main", __name__,)


@main_blueprint.route("/", methods=["GET"])
def home():
  return render_template("main/home.html")


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
