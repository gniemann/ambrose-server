from flask import Blueprint, render_template, abort, redirect, url_for, request

from devops_monitor.common import cipher_required
from devops_monitor.services import UserService, UserCredentialMismatchException, DevOpsAccountService, \
    UnauthorizedAccessException
from .forms import LoginForm, RegisterForm, MessageForm, DevOpsAccountForm, create_edit_form

web_bp = Blueprint('web', __name__, template_folder='templates')


@web_bp.route('/')
@UserService.auth_required
def index(user):
    return render_template('index.html', lights=user.lights)


@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        try:
            UserService.login(login_form.username.data, login_form.password.data)
        except UserCredentialMismatchException:
            abort(401)

        return redirect(url_for('.index'))

    return render_template('login.html', login_form=login_form, register_form=RegisterForm())


@web_bp.route('/register', methods=['POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        UserService.create_user(form.username.data, form.password.data)
        return redirect(url_for('.index'))

    return redirect(url_for('.login'))


@web_bp.route('/logout')
@UserService.auth_required
def logout(user):
    UserService.logout()
    return redirect(url_for('.login'))


@web_bp.route('/messages', methods=['GET', 'POST'])
@UserService.auth_required
def messages(user):
    message_form = MessageForm()

    if message_form.validate_on_submit():
        UserService.add_message(user, message_form.message.data)

    return render_template('messages.html', message_form=message_form, messages=user.messages)


@web_bp.route('/messages/clear', methods=['POST'])
@UserService.auth_required
def clear_messages(user):
    UserService.clear_messages(user)
    return redirect(url_for('.messages'))


@web_bp.route('/accounts', methods=['GET', 'POST'])
@UserService.auth_required
@cipher_required
def accounts(user, cipher):
    new_account_form = DevOpsAccountForm(data={'username': user.username})

    if new_account_form.validate_on_submit():
        DevOpsAccountService(cipher).new_account(
            user,
            new_account_form.username.data,
            new_account_form.organization.data,
            new_account_form.token.data,
            new_account_form.nickname.data
        )

        new_account_form = DevOpsAccountForm(data={'username': user.username})

    return render_template('accounts.html', new_account_form=new_account_form, accounts=user.accounts)


@web_bp.route('/accounts/<account_id>/tasks', methods=['GET', 'POST'])
@UserService.auth_required
@cipher_required
def account_tasks(account_id, user, cipher):
    account_service = DevOpsAccountService(cipher)
    account = None
    try:
        account = account_service.get_account(account_id, user)
    except UnauthorizedAccessException:
        abort(403)

    if request.method == 'POST':
        # TODO: WTForms to clean this up (somehow)
        task_data = {task:dict() for task in [key for key, val in request.form.items() if val == 'on']}

        for task in task_data:
            raw_properties = [val for val in request.form if val.startswith(task + '_')]
            task_data[task] = {prop.split('_', maxsplit=1)[1]: request.form[prop] for prop in raw_properties}

        account_service.update_tasks(account, task_data)

        return redirect(url_for('.index'))

    current_build_tasks = account_service.build_tasks(account)
    current_release_tasks = account_service.release_tasks(account)
    tasks = account_service.list_all_tasks(account)

    current_tasks = current_build_tasks.union(current_release_tasks)
    return render_template('tasks.html', tasks=tasks, current_tasks=current_tasks, account_id=account_id)


@web_bp.route('/edit', methods=['GET', 'POST'])
@UserService.auth_required
def edit(user):
    edit_form = create_edit_form(user.lights, user.tasks)

    if edit_form.validate_on_submit():
        UserService.update_lights(user, edit_form.data)
        # regenerate the form, in case there were size changes
        edit_form = create_edit_form(user.lights, user.tasks)

    return render_template('edit.html', form=edit_form)
