import functools
from collections import namedtuple

from flask import Blueprint, render_template, abort, redirect, url_for, current_app
import flask_login
import flask_bcrypt as bcrypt
from cryptography.fernet import Fernet

from devops_monitor.models import User, db
from devops import DevOpsService, Credentials
from .forms import LoginForm, RegisterForm, SettingsForm, SetupForm

login_manager = flask_login.LoginManager()
login_manager.login_view = 'web.login'

web_bp = Blueprint('web', __name__, template_folder='templates')

AvailableTask = namedtuple('Task', 'id name type')

class WebUser(flask_login.UserMixin):
    pass


def cipher_required(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        cipher = Fernet(current_app.secret_key)
        return func(*args, cipher=cipher, **kwargs)

    return inner


def db_required(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            resp = func(*args, session=db.session, **kwargs)
            db.session.commit()
            return resp
        except:
            db.session.rollback()
            raise

    return inner

@login_manager.user_loader
def load_user(username):
    user = User.by_username(username)

    if not user:
        return None

    web_user = WebUser()
    web_user.id = username
    return web_user


@web_bp.route('/')
@flask_login.login_required
def index():
    user = User.by_username(flask_login.current_user.id)

    return render_template('index.html', tasks=user.tasks)


@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        user = User.by_username(login_form.username.data)
        if not user or not bcrypt.check_password_hash(user.password, login_form.password.data):
            abort(401)

        web_user = WebUser()
        web_user.id = user.username
        flask_login.login_user(web_user)

        return redirect(url_for('.index'))

    return render_template('login.html', login_form=login_form, register_form=RegisterForm())

@web_bp.route('/register', methods=['POST'])
@cipher_required
@db_required
def register(cipher, session):
    form = RegisterForm()

    if form.validate_on_submit():
        if form.password.data != form.confirm_password.data:
            abort(400)

        user = User(username=form.username.data, organization=form.organization.data)
        user.password = bcrypt.generate_password_hash(form.password.data)

        user.token = cipher.encrypt(form.token.data.encode('utf-8'))

        session.add(user)

        web_user = WebUser()
        web_user.id = user.username
        flask_login.login_user(web_user)

        return redirect(url_for('.setup'))

    return redirect(url_for('.login'))

@web_bp.route('/setup', methods=['GET', 'POST'])
@flask_login.login_required
@cipher_required
def setup(cipher):
    setup_form = SetupForm()
    tasks = None

    if setup_form.validate_on_submit():
        user = User.by_username(flask_login.current_user.id)
        token = cipher.decrypt(user.token)

        service = DevOpsService(Credentials(user.username, token))
        project = setup_form.project.data

        tasks = []
        release_list = service.list_release_definitions(user.organization, project)
        if release_list:
            for release in release_list['value']:
                release_id = release['id']
                summary = service.get_release_summary(user.organization, project, release_id)
                tasks.extend([AvailableTask(id=release_id, name=name, type='release') for name in summary])

        builds = service.list_build_definitions(user.organization, project)
        if builds:
            tasks.extend([AvailableTask(id=b['id'], name=b['name'], type='build') for b in builds['value']])


    return render_template('setup.html', setup_form=setup_form, tasks=tasks, configured_tasks=user.tasks)

@web_bp.route('/settings', methods=['GET', 'POST'])
@flask_login.login_required
def settings():
    settings_form = SettingsForm()
    user = User.by_username(flask_login.current_user.id)

    if settings_form.validate_on_submit():
        return redirect(url_for('.index'))

    settings_form.username.data = user.username
    return render_template('settings.html', form=settings_form)

@web_bp.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for('.login'))
