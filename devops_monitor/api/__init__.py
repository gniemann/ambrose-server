import os

from flask import Blueprint, jsonify, abort

from devops import DevOpsService, Credentials
from devops_monitor.models import User

api_bp = Blueprint('api', __name__)

@api_bp.route('/status/releases')
def get_release_status():
    username = os.getenv('DEVOPS_USERNAME')
    token = os.getenv('DEVOPS_TOKEN')
    service = DevOpsService(Credentials(username, token))
    user = User.by_username(username)

    if not user:
        abort(404)

    retVal = build_release_statuses(user, service)
    return jsonify(retVal)


def build_release_statuses(user, service):
    task_set = set([(t.project, t.definitionId) for t in user.tasks if t.type == 'release'])

    summary = {}
    for (project, definition) in task_set:
        summary.update(service.get_release_summary(user.organization, project, definition))

    return [summary.get(task.name, dict()) for task in user.tasks if task.type == 'release']