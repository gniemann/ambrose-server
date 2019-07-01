from flask import Blueprint, render_template

from ambrose.models import User, Device
from ambrose.services import AuthService, UserService
from .forms import create_edit_form

devices_bp = Blueprint('devices', __name__, template_folder='templates')


@devices_bp.route('/')
@AuthService.auth_required
def index(user: User):
    token = AuthService.jwt(user)
    return render_template('devices.html', devices=user.devices, jwt=token)


@devices_bp.route('/<int:device_id>/lights', methods=['GET', 'POST'])
@AuthService.auth_required
def edit_lights(device_id: int, user: User, user_service: UserService):
    device = Device.by_id(device_id)
    edit_form = create_edit_form(device.lights, user.tasks)

    if edit_form.validate_on_submit():
        user_service.update_lights(device_id, edit_form.data)
        # regenerate the form, in case there were size changes
        edit_form = create_edit_form(device.lights, user.tasks)

    return render_template('edit.html', form=edit_form, device_id=device.id)