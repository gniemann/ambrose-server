import functools

from flask import Blueprint, abort, request, jsonify
import flask_bcrypt as bcrypt

from devops import DevOpsService, Credentials
from devops_monitor.models import User
from devops_monitor.common import cipher_required
from .schema import TaskSchema, StatusSchema, with_schema

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
@with_schema(TaskSchema)
@authorization_required
@cipher_required
def get_release_status(user, cipher):
    service = get_service(user, cipher)

    releases = release_statuses(user, service)
    return build_summary(releases, user.tasks, 'release')


def task_set(tasks, task_type):
    return set([(t.project, t.definitionId) for t in tasks if t.type == task_type])

def build_summary(summary, tasks, task_type):
    return [summary.get(task.name, dict()) for task in tasks if task.type == task_type]

def release_statuses(user, service):
    summary = {}
    for (project, definition) in task_set(user.tasks, 'release'):
        summary.update(service.get_release_statuses(user.organization, project, definition))

    return summary


@api_bp.route('/status/builds')
@with_schema(TaskSchema)
@authorization_required
@cipher_required
def get_build_status(user, cipher):
    service = get_service(user, cipher)

    builds = build_statuses(user, service)
    return build_summary(builds, user.tasks, 'build')

def build_statuses(user, service):
    summary = {}
    tasks = task_set(user.tasks, 'build')
    projects = set([p for (p, _) in tasks])
    for project in projects:
        definitions = [d for (p, d) in tasks if p == project]
        summary.update(service.get_build_statuses(user.organization, project, definitions))

    return summary

@api_bp.route('/status')
@with_schema(StatusSchema)
@authorization_required
@cipher_required
def get_status(user, cipher):
    service = get_service(user, cipher)

    releases = release_statuses(user, service)
    builds = build_statuses(user, service)
    combined = releases
    combined.update(builds)

    tasks = [combined.get(t.name, dict())._asdict() for t in user.tasks]
    messages = [
        "Hello world!",
        "All OK Jumpmaster"
    ]
    return {
        "tasks": tasks,
        "messages": messages
    }