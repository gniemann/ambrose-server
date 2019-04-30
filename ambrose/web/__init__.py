from flask import Blueprint, render_template, abort, redirect, url_for

from ambrose.models import User
from ambrose.services import UserService, UserCredentialMismatchException, AuthService
from .forms import LoginForm, RegisterForm, DevOpsAccountForm, create_edit_form, NewTaskForm
from .tasks import tasks_bp
from .accounts import accounts_bp
from .messages import messages_bp
from .gauges import gauges_bp

web_bp = Blueprint('web', __name__, template_folder='templates')


@web_bp.route('/')
@AuthService.auth_required
def index(user: User):
    token = AuthService.jwt(user)
    return render_template('index.html', lights=user.lights, messages=user.messages, jwt=token)


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


@web_bp.route('/edit', methods=['GET', 'POST'])
@AuthService.auth_required
def edit(user: User, user_service: UserService):
    edit_form = create_edit_form(user.lights, user.tasks)

    if edit_form.validate_on_submit():
        user_service.update_lights(edit_form.data)
        # regenerate the form, in case there were size changes
        edit_form = create_edit_form(user.lights, user.tasks)

    return render_template('edit.html', form=edit_form)