from typing import Any, Dict

from flask import Blueprint, request, abort

from ambrose.api.devices import Devices
from ambrose.models import User
from ambrose.services import LightService, AuthService, UserCredentialMismatchException, \
    UserService
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
register_api(Devices, 'devices', pk='device_id')


@api_bp.route('/status')
@with_schema(StatusSchema)
@AuthService.auth_required
def get_status(user: User, user_service: UserService) -> Dict[str, Any]:
    retval = {
        "lights": LightService.lights_for_user(user),
        "messages": [m.value for m in user.messages],
        'gauges': user.gauges
    }

    user_service.mark_tasks_viewed()
    return retval


@api_bp.route('/login', methods=['POST'])
@with_schema(AccessTokenSchema)
def login():
    credentials = LoginSchema().load(request.json)
    try:
        user = AuthService.login(credentials['username'], credentials['password'])
    except UserCredentialMismatchException:
        abort(401)

    return {
        'access_token': AuthService.jwt(user)
    }


@api_bp.route('/devices/register', methods=['POST'])
@AuthService.auth_required
@with_schema(AccessTokenSchema)
def register_device(user_service: UserService):
    name = request.json['name']
    device = user_service.add_device(name)

    return {
        'access_token': AuthService.jwt(device)
    }
