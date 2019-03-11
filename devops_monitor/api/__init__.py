from concurrent import futures
from typing import Any, Dict

from cryptography.fernet import Fernet
from flask import Blueprint, request, abort

from devops_monitor.common import cipher_required
from devops_monitor.models import User
from devops_monitor.services import LightService, AccountService, AuthService, UserCredentialMismatchException
from .schema import TaskSchema, StatusSchema, with_schema, LoginSchema, AccessTokenSchema
from .messages import Messages
from .tasks import Tasks

api_bp = Blueprint('api', __name__)


def register_api(view, endpoint, pk='id', pk_type='int'):
    view_func = view.as_view(endpoint)
    url = '/{}/'.format(endpoint)
    api_bp.add_url_rule(url, defaults={pk: None},
                     view_func=view_func, methods=['GET',])
    api_bp.add_url_rule(url, view_func=view_func, methods=['POST',])
    api_bp.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                     methods=['GET', 'PUT', 'DELETE'])


register_api(Messages, 'messages', pk='message_id')
register_api(Tasks, 'tasks', pk='task_id')

@api_bp.route('/status')
@with_schema(StatusSchema)
@AuthService.auth_required
@cipher_required
def get_status(user: User, cipher: Fernet) -> Dict[str, Any]:
    for account in user.accounts:
        AccountService(account, cipher).get_task_statuses()

    return {
        "lights": LightService.lights_for_user(user),
        "messages": [m.value for m in user.messages],
        'gauges': user.gauges
    }

@api_bp.route('/login', methods=['POST'])
@with_schema(AccessTokenSchema)
def login():
    credentials = LoginSchema().load(request.json)
    try:
        user = AuthService.login(credentials['username'], credentials['password'])
    except UserCredentialMismatchException:
        abort(401)

    retval = {
        'access_token': AuthService.jwt(user)
    }

    return retval