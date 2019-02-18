from flask import Blueprint, render_template, abort, redirect, url_for, request

from devops_monitor.services import UserService, UserCredentialMismatchException
from .forms import LoginForm, RegisterForm, MessageForm, DevOpsAccountForm, create_edit_form, NewTaskForm
from .tasks import tasks_bp
from .accounts import accounts_bp

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



@web_bp.route('/edit', methods=['GET', 'POST'])
@UserService.auth_required
def edit(user):
    edit_form = create_edit_form(user.lights, user.tasks)

    if edit_form.validate_on_submit():
        UserService.update_lights(user, edit_form.data)
        # regenerate the form, in case there were size changes
        edit_form = create_edit_form(user.lights, user.tasks)

    return render_template('edit.html', form=edit_form)
