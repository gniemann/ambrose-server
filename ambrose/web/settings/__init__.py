from flask import Blueprint, render_template, redirect, url_for

from ambrose.models import User
from ambrose.services import AuthService
from services import UserService
from .forms import LightSettingsForm

settings_bp = Blueprint('settings', __name__, template_folder='templates')


@settings_bp.route('/', methods=['GET', 'POST'])
@AuthService.auth_required
def index(user: User, user_service: UserService):
    light_form = LightSettingsForm()

    if light_form.validate_on_submit():
        user_service.add_setting(light_form.status.data, light_form.red.data, light_form.green.data, light_form.blue.data)

        return redirect(url_for('.index'))

    return render_template('settings.html', settings=user.light_settings, form=light_form)
