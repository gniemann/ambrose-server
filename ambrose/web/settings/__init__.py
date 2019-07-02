from flask import Blueprint, render_template, redirect, url_for

from ambrose.models import User
from ambrose.services import AuthService
from services import UserService
from .forms import LightSettingsForm, EditSettingsForm

settings_bp = Blueprint('settings', __name__, template_folder='templates')


@settings_bp.route('/', methods=['GET', 'POST'])
@AuthService.auth_required
def index(user: User, user_service: UserService):
    settings = [{'status': s.status,
                 'red': s.color_red,
                 'green': s.color_green,
                 'blue': s.color_blue,
                 'setting_id': s.id} for s in user.light_settings]

    edit_form = EditSettingsForm(data={'settings': settings})

    if edit_form.validate_on_submit():
        user_service.edit_settings(edit_form.settings.data)

        return redirect(url_for('.index'))

    return render_template('settings.html',edit_form=edit_form, new_form=LightSettingsForm())


@settings_bp.route('/new', methods=['POST'])
@AuthService.auth_required
def new_setting(user_service: UserService):
    light_form = LightSettingsForm()

    if light_form.validate_on_submit():
        user_service.add_setting(light_form.status.data,
                                 light_form.red.data,
                                 light_form.green.data,
                                 light_form.blue.data)

    return redirect(url_for('.index'))
