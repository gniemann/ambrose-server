from collections import namedtuple

from flask import Blueprint, render_template, abort, redirect, url_for, request
import flask_bcrypt as bcrypt
import flask_login

from devops import DevOpsService
from devops_monitor.models import User, Message, Task, DevOpsAccount, Account, DevOpsBuildPipeline, \
    DevOpsReleaseEnvironment
from devops_monitor.common import cipher_required, db_required, WebUser
from .forms import LoginForm, RegisterForm, SettingsForm, MessageForm, DevOpsAccountForm

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

        user = User(username=form.username.data)
        user.password = bcrypt.generate_password_hash(form.password.data)

        session.add(user)

        web_user = WebUser()
        web_user.id = user.username
        flask_login.login_user(web_user)

        return redirect(url_for('.index'))

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

@web_bp.route('/accounts', methods=['GET', 'POST'])
@flask_login.login_required
@db_required
@cipher_required
def accounts(session, cipher):
    user = User.by_username(flask_login.current_user.id)

    new_account_form = DevOpsAccountForm(data={'username': user.username})

    if new_account_form.validate_on_submit():
        account = DevOpsAccount(
            username=new_account_form.username.data,
            organization=new_account_form.organization.data,
            nickname=new_account_form.nickname.data
        )

        account.token = cipher.encrypt(new_account_form.token.data.encode('utf-8'))
        user.accounts.append(account)

        new_account_form = DevOpsAccountForm(data={'username': user.username})

        session.commit()

    return render_template('accounts.html', new_account_form=new_account_form, accounts=user.accounts)

BuildTask = namedtuple('BuildTask', 'project definition_id name type')
ReleaseTask = namedtuple('ReleaseTask', 'project definition_id name environment environment_id type')

@web_bp.route('/accounts/<account_id>/tasks', methods=['GET', 'POST'])
@flask_login.login_required
@db_required
@cipher_required
def account_tasks(account_id, session, cipher):
    account = Account.by_id(account_id)
    user = User.by_username(flask_login.current_user.id)
    if account not in user.accounts:
        abort(403)

    current_build_tasks = set()
    for task in [t for t in account.tasks if isinstance(t, DevOpsBuildPipeline)]:
        current_build_tasks.add(BuildTask(
            project=task.project,
            definition_id=task.definition_id,
            name=task.pipeline,
            type='build'
        ))

    current_release_tasks = set()
    for task in [t for t in account.tasks if isinstance(t, DevOpsReleaseEnvironment)]:
        current_release_tasks.add(ReleaseTask(
            project=task.project,
            definition_id=task.definition_id,
            name=task.pipeline,
            environment=task.environment,
            environment_id=task.environment_id,
            type='release'
        ))

    if request.method == 'POST':
        selected_tasks = set([key for key, val in request.form.items() if val == 'on'])

        build_tasks = set()
        for build in [t for t in selected_tasks if t.startswith('build')]:
            build_tasks.add(BuildTask(
                project=request.form[build + '_project'],
                definition_id=int(request.form[build + '_definition_id']),
                name=request.form[build + '_name'],
                type='build'
            ))

        # tasks to remove
        for task in current_build_tasks.difference(build_tasks):
            account.remove_task(task)

        # tasks to add
        for task in build_tasks.difference(current_build_tasks):
            account.add_task(DevOpsBuildPipeline(
               project=task.project,
               definition_id=task.definition_id,
               pipeline=task.name
            ))


        release_tasks = set()
        for release in [t for t in selected_tasks if t.startswith('release')]:
            release_tasks.add(ReleaseTask(
                project=request.form[release + '_project'],
                definition_id=int(request.form[release + '_definition_id']),
                name=request.form[release + '_name'],
                environment=request.form[release + '_environment'],
                environment_id=int(request.form[release + '_environment_id']),
                type='release'
            ))

        # tasks to remove
        for task in current_release_tasks.difference(release_tasks):
            account.remove_task(task)

        #tasks to add
        for task in release_tasks.difference(current_release_tasks):
            account.add_task(DevOpsReleaseEnvironment(
                project=task.project,
                definition_id=task.definition_id,
                pipeline=task.name,
                environment=task.environment,
                environment_id=task.environment_id
            ))

        return redirect(url_for('.index'))

    token = cipher.decrypt(account.token)
    service = DevOpsService(account.username, token, account.organization)
    project_list = service.list_projects()
    if not project_list:
        abort(400)

    tasks = []

    for project in [p.name for p in project_list]:
        release_list = service.list_release_definitions(project)
        if release_list:
            for release in release_list:
                for environment in release.environments:
                    tasks.append(ReleaseTask(
                        project=project,
                        definition_id=release.id,
                        name=release.name,
                        environment=environment.name,
                        environment_id=environment.id,
                        type='release'
                    ))

        build_list = service.list_build_definitions(project)
        if build_list:
            for build in build_list:
                tasks.append(BuildTask(
                    project=project,
                    definition_id=build.id,
                    name=build.name,
                    type='build'
                ))

        session.commit()

    current_tasks = current_build_tasks.union(current_release_tasks)
    return render_template('tasks.html', tasks=tasks, current_tasks=current_tasks, account_id=account_id)
