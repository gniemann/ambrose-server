from flask import Blueprint

from devops_monitor.common import cipher_required
from devops_monitor.services import LightService, AccountService, AuthService
from .schema import TaskSchema, StatusSchema, with_schema

api_bp = Blueprint('api', __name__)


@api_bp.route('/status')
@with_schema(StatusSchema)
@AuthService.auth_required
@cipher_required
def get_status(user, cipher):
    for account in user.accounts:
        AccountService(account, cipher).get_task_statuses()

    return {
        "lights": LightService.lights_for_user(user),
        "messages": [m.value.upper() for m in user.messages]
    }