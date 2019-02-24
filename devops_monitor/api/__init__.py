from typing import Any, Dict

import jwt
from cryptography.fernet import Fernet
from flask import Blueprint, make_response, request, current_app, abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required

from devops_monitor.common import cipher_required
from devops_monitor.models import User
from devops_monitor.services import LightService, AccountService, AuthService, UserService
from .schema import TaskSchema, StatusSchema, with_schema

api_bp = Blueprint('api', __name__)


@api_bp.route('/status')
@with_schema(StatusSchema)
@AuthService.auth_required
@cipher_required
def get_status(user: User, cipher: Fernet) -> Dict[str, Any]:
    for account in user.accounts:
        AccountService(account, cipher).get_task_statuses()

    return {
        "lights": LightService.lights_for_user(user),
        "messages": [m.value.upper() for m in user.messages]
    }


class Messages(MethodView):
    decorators = [jwt_required]

    def get(self, message_id):
        pass

    def delete(self, message_id):
        user = AuthService.current_api_user()
        if not user:
            abort(401)

        UserService(user).delete_message(message_id)
        return 'No content', 204


message_view = Messages.as_view('messages')
api_bp.add_url_rule('/messages/<int:message_id>', view_func=message_view, methods=['DELETE'])
api_bp.add_url_rule('/messages/', defaults={'message_id': None}, view_func=message_view, methods=['GET'])
