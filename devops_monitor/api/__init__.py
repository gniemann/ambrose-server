import functools

from flask import Blueprint, jsonify, abort, request
import flask_bcrypt as bcrypt

from devops import DevOpsService, Credentials, determine_build_statuses, determine_release_statuses, BuildStatus, ReleaseStatus
from devops_monitor.models import User
from devops_monitor.common import cipher_required

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


def get_service(user, cipher):
    token = cipher.decrypt(user.token)
    return DevOpsService(Credentials(user.username, token))


@api_bp.route('/status/releases')
@authorization_required
@cipher_required
def get_release_status(user, cipher):
    service = get_service(user, cipher)

    releases = release_statuses(user, service)
    retVal = build_summary(releases, user.tasks, 'release', ReleaseStatus)
    return jsonify(retVal)


def task_set(tasks, task_type):
    return set([(t.project, t.definitionId) for t in tasks if t.type == task_type])

def build_summary(summary, tasks, task_type, missing):
    return [summary.get(task.name, missing())._asdict() for task in tasks if task.type == task_type]

def release_statuses(user, service):
    summary = {}
    for (project, definition) in task_set(user.tasks, 'release'):
        release_summary = service.get_release_summary(user.organization, project, definition)
        summary.update(determine_release_statuses(release_summary))

    return summary


@api_bp.route('/status/builds')
@authorization_required
@cipher_required
def get_build_status(user, cipher):
    service = get_service(user, cipher)

    builds = build_statuses(user, service)
    retVal = build_summary(builds, user.tasks, 'build', BuildStatus)
    return jsonify(retVal)

def build_statuses(user, service):
    summary = {}
    tasks = task_set(user.tasks, 'build')
    projects = set([p for (p, _) in tasks])
    for project in projects:
        definitions = [d for (p, d) in tasks if p == project]
        build = service.get_build_summary(user.organization, project, definitions)
        summary.update(determine_build_statuses(build))

    return summary

@api_bp.route('/status')
@authorization_required
@cipher_required
def get_status(user, cipher):
    service = get_service(user, cipher)

    releases = release_statuses(user, service)
    builds = build_statuses(user, service)
    combined = releases
    combined.update(builds)

    tasks = [combined.get(t.name, dict())._asdict() for t in user.tasks]
    messages = ["Hello world!"]
    retval = {
        "tasks": tasks,
        "messages": messages
    }
    return jsonify(retval)