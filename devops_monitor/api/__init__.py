import functools

from flask import Blueprint, abort, request
import flask_bcrypt as bcrypt

from devops_monitor.models import User
from devops_monitor.common import cipher_required
from devops_monitor.services import DevOpsAccountService, LightService
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


@api_bp.route('/status')
@with_schema(StatusSchema)
@authorization_required
@cipher_required
def get_status(user, cipher):
    account = user.devops_account
    if not account:
        abort(404)

    # DevOpsAccountService(cipher).get_task_statuses(account)

    return {
        "lights": LightService.lights_for_user(user),
        "messages": [m.upper() for m in user.messages]
    }