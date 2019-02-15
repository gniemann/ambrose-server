from collections import namedtuple

from flask import Blueprint, render_template, abort, redirect, url_for, request
import flask_bcrypt as bcrypt
import flask_login

from devops import DevOpsService, Credentials
from devops_monitor.models import User, Message, Task
from devops_monitor.common import cipher_required, db_required, WebUser
from .forms import LoginForm, RegisterForm, SettingsForm, SetupForm, MessageForm

web_bp = Blueprint('web', __name__, template_folder='templates')

AvailableTask = namedtuple('Task', 'id name type monitored sort_order')

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

@web_bp.route('/messages', methods=['GET', 'POST'])
@flask_login.login_required
@db_required
def messages(session):
    user = User.by_username(flask_login.current_user.id)

    message_form = MessageForm()

    if message_form.validate_on_submit():
        user.messages.append(Message(text=message_form.message.data))

    current_messages = [m.text for m in user.messages]

    return render_template('messages.html', message_form=message_form, messages=current_messages)

@web_bp.route('/messages/clear', methods=['POST'])
@flask_login.login_required
@db_required
def clear_messages(session):
    user = User.by_username(flask_login.current_user.id)
    user.messages.clear()

    return redirect(url_for('.messages'))

@web_bp.route('/setup', methods=['GET', 'POST'])
@flask_login.login_required
@cipher_required
def setup(cipher):
    setup_form = SetupForm()
    tasks = []
    project = None

    user = User.by_username(flask_login.current_user.id)

    if setup_form.validate_on_submit():
        token = cipher.decrypt(user.token)

        service = DevOpsService(Credentials(user.username, token))
        project = setup_form.project.data

        current_tasks = {t.name: t.sort_order for t in user.tasks}

        release_list = service.list_release_definitions(user.organization, project)
        if release_list:
            for release in release_list.value:
                release_id = release.id
                summary = service.get_release_summary(user.organization, project, release_id)

                if not summary:
                    continue

                tasks.extend([AvailableTask(id=release_id, name=name, type='release', monitored=name in current_tasks, sort_order=current_tasks.get(name)) for name in summary.environment_names()])

        builds = service.list_build_definitions(user.organization, project)
        if builds:
            tasks.extend([AvailableTask(id=b.id, name=b.name, type='build', monitored=b.name in current_tasks, sort_order=current_tasks.get(b.name)) for b in builds.value])


    tasks.sort(key=lambda t: t.sort_order if isinstance(t.sort_order, int) else 1000)

    return render_template('setup.html', setup_form=setup_form, tasks=tasks, project_id=project)

@web_bp.route('/setup/pipelines', methods=['POST'])
@flask_login.login_required
@db_required
def setup_pipelines(session):
    user = User.by_username(flask_login.current_user.id)

    project = request.form['project']
    selected_task_names = set([name for name, val in request.form.items() if val == 'on'])

    current_task_names = set([t.name for t in user.tasks])
    tasks_to_remove = current_task_names.difference(selected_task_names)
    tasks_to_add = selected_task_names.difference(current_task_names)
    tasks_to_update = selected_task_names.intersection(current_task_names)

    user.remove_tasks(tasks_to_remove)

    new_tasks = [Task(project=project, type=request.form[name + '_type'], sort_order=request.form[name + '_sortOrder'], definitionId=request.form[name + '_id'], name=name) for name in tasks_to_add]
    user.add_tasks(new_tasks)

    for name in tasks_to_update:
        for task in user.tasks:
            if task.name != name:
                continue
            task.sort_order = request.form[name + '_sortOrder']
            break

    return redirect(url_for('.index'))