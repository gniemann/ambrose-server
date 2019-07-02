from flask import Blueprint, render_template, abort, redirect, url_for

from ambrose.models import User
from ambrose.services import UserService, UserCredentialMismatchException, AuthService
from .forms import LoginForm, RegisterForm, LightSettingForm
from .tasks import tasks_bp
from .accounts import accounts_bp
from .messages import messages_bp
from .gauges import gauges_bp
from .devices import devices_bp

web_bp = Blueprint('web', __name__, template_folder='templates')


@web_bp.route('/')
@AuthService.auth_required
def index(user: User):
    token = AuthService.jwt(user)
    return render_template('index.html', user=user, messages=user.messages, jwt=token)


@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        try:
            AuthService.login(login_form.username.data, login_form.password.data)
        except UserCredentialMismatchException:
            abort(401)

        return redirect(url_for('.index'))

    return render_template('login.html', login_form=login_form, register_form=RegisterForm())


@web_bp.route('/register', methods=['POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        user = UserService.create_user(form.username.data, form.password.data)
        AuthService.login_user(user)
        return redirect(url_for('.index'))

    return redirect(url_for('.login'))


@web_bp.route('/logout')
@AuthService.auth_required
def logout():
    AuthService.logout()
    return redirect(url_for('.login'))


@web_bp.route('/settings', methods=['GET', 'POST'])
@AuthService.auth_required
def settings(user: User, user_service: UserService):
    light_form = LightSettingForm()

    if light_form.validate_on_submit():
        user_service.add_setting(light_form.status.data, light_form.red.data, light_form.green.data, light_form.blue.data)

        light_form = LightSettingForm()


    return render_template('settings.html', settings=user.light_settings, form=light_form)