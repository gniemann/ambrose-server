import functools
import os

from flask import Blueprint, jsonify, abort, request, current_app
import flask_bcrypt as bcrypt
from cryptography.fernet import Fernet

from devops import DevOpsService, Credentials
from devops_monitor.models import User

api_bp = Blueprint('api', __name__)

def authorization_required(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        if not request.authorization:
            abort(401)
        user = User.by_username(request.authorization.username)

        if user and bcrypt.check_password_hash(user.password, request.authorization.password):

            return func(*args, user=user, **kwargs)
        else:
            abort(401)

    return inner


def get_service(user):
    cipher = Fernet(current_app.config['SECRET_KEY'])
    token = cipher.decrypt(user.token.encode('utf-8'))
    return DevOpsService(Credentials(user.username, token))

@api_bp.route('/status/releases')
@authorization_required
def get_release_status(user):
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
@authorization_required
def get_build_status(user):
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
@authorization_required
def get_status(user):
    service = get_service(user)

    releases = release_statuses(user, service)
    builds = build_statuses(user, service)
    combined = releases
    combined.update(builds)

    retVal = [combined.get(t.name, dict()) for t in user.tasks]
    return jsonify(retVal)