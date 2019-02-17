import functools

from flask import Blueprint, abort, request
import flask_bcrypt as bcrypt

from devops import DevOpsService
from devops_monitor.models import User, DevOpsReleaseEnvironment, DevOpsBuildPipeline
from devops_monitor.common import cipher_required, db_required
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


def get_devops_service(user, cipher):
    devops_account = user.devops_account

    if not devops_account:
        return None

    token = devops_account.token
    if not isinstance(token, bytes):
        token = token.encode('utf-8')

    token = cipher.decrypt(token)
    return DevOpsService(devops_account.username, token, devops_account.organization)


def task_set(tasks, task_type):
    return set([(t.project, t.definitionId) for t in tasks if isinstance(t, task_type)])


def release_statuses(user, service):
    devops_account = user.devops_account
    if not devops_account:
        return

    releases = [t for t in devops_account.tasks if isinstance(t, DevOpsReleaseEnvironment)]
    for (project, definition) in set([(t.project, t.definition_id) for t in releases]):
        statuses = service.get_release_summary(project, definition)
        for env in [r for r in releases if r.project == project and r.definition_id == definition]:
            env.status = statuses.status_for_environment(env.environment_id)


def build_statuses(user, service):
    devops_account = user.devops_account
    if not devops_account:
        return

    builds = [t for t in devops_account.tasks if isinstance(t, DevOpsBuildPipeline)]
    for project in set([b.project for b in builds]):
        project_builds = [b for b in builds if b.project == project]
        definitions = [b.definition_id for b in project_builds]
        statuses = service.get_build_summary(project, definitions)

        for build in project_builds:
            build.status = statuses.status_for_definition(build.definition_id)


@api_bp.route('/status')
@with_schema(StatusSchema)
@authorization_required
@db_required
@cipher_required
def get_status(user, session, cipher):
    service = get_devops_service(user, cipher)

    release_statuses(user, service)
    build_statuses(user, service)

    return {
        "tasks": user.tasks,
        "messages": [m.text.upper() for m in user.messages]
    }