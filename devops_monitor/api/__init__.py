import os

from flask import Blueprint, jsonify, abort

from devops import DevOpsService, Credentials
from devops_monitor.models import User

api_bp = Blueprint('api', __name__)

def get_user():
    username = os.getenv('DEVOPS_USERNAME')
    return User.by_username(username)

def get_service(user):
    token = os.getenv('DEVOPS_TOKEN')
    return DevOpsService(Credentials(user.username, token))

@api_bp.route('/status/releases')
def get_release_status():
    user = get_user()
    if not user:
        abort(404)

    service = get_service(user)

    releases = release_statuses(user, service)
    retVal = build_summary(releases, user.tasks, 'release')
    return jsonify(retVal)


def task_set(tasks, task_type):
    return set([(t.project, t.definitionId) for t in tasks if t.type == task_type])

def build_summary(summary, tasks, task_type):
    return [summary.get(task.name, dict()) for task in tasks if task.type == task_type]

def release_statuses(user, service):
    summary = {}
    for (project, definition) in task_set(user.tasks, 'release'):
        summary.update(service.get_release_summary(user.organization, project, definition))

    return summary


@api_bp.route('/status/builds')
def get_build_status():
    user = get_user()
    if not user:
        abort(404)

    service = get_service(user)

    builds = build_statuses(user, service)
    retVal = build_summary(builds, user.tasks, 'build')
    return jsonify(retVal)

def build_statuses(user, service):
    summary = {}
    tasks = task_set(user.tasks, 'build')
    projects = set([p for (p, _) in tasks])
    for project in projects:
        definitions = [d for (p, d) in tasks if p == project]
        summary.update(service.get_build_summary(user.organization, project, definitions))

    return summary

@api_bp.route('/status')
def get_status():
    user = get_user()
    if not user:
        abort(404)

    service = get_service(user)

    releases = release_statuses(user, service)
    builds = build_statuses(user, service)
    combined = releases
    combined.update(builds)

    retVal = [combined.get(t.name, dict()) for t in user.tasks]
    return jsonify(retVal)