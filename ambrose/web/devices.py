from flask import Blueprint, render_template

from ambrose.models import User
from ambrose.services import AuthService

devices_bp = Blueprint('devices', __name__, template_folder='templates/devices')


@devices_bp.route('/')
@AuthService.auth_required
def index(user: User):
    token = AuthService.jwt(user)
    return render_template('devices.html', devices=user.devices, jwt=token)
