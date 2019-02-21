from flask import Blueprint

from devops_monitor.models import DevOpsAccount, ApplicationInsightsAccount
from devops_monitor.common import cipher_required
from devops_monitor.services import DevOpsAccountService, LightService, UserService, ApplicationInsightsAccountService
from .schema import TaskSchema, StatusSchema, with_schema

api_bp = Blueprint('api', __name__)


@api_bp.route('/status')
@with_schema(StatusSchema)
@UserService.auth_required
@cipher_required
def get_status(user, cipher):
    for account in user.accounts:
        if isinstance(account, DevOpsAccount):
            DevOpsAccountService(cipher).get_task_statuses(account)
        if isinstance(account, ApplicationInsightsAccount):
            ApplicationInsightsAccountService(cipher).update_task_statuses(account)

    return {
        "lights": LightService.lights_for_user(user),
        "messages": [m.value.upper() for m in user.messages]
    }