from flask import Blueprint, render_template, url_for, redirect

from devops_monitor.common import db_transaction
from devops_monitor.services import UserService, AuthService
from devops_monitor.web.forms import NewMessageForm, DateTimeMessageForm, MessageForm, TaskMessageForm

messages_bp = Blueprint('messages', __name__, template_folder='templates/messages')


@messages_bp.route('/', methods=['GET', 'POST'])
@AuthService.auth_required
def index(user):
    form = NewMessageForm()
    form.type.choices = [
        ('text', 'Static text'),
        ('datetime', 'Datetime'),
        ('task', 'Task status')
    ]

    if form.validate_on_submit():
        message_type = form.type.data
        return redirect(url_for('.new_message', message_type=message_type))

    return render_template('messages.html', form=form, messages=user.messages)


@messages_bp.route('/new/<message_type>', methods=['GET', 'POST'])
@AuthService.auth_required
def new_message(message_type, user):
    form = message_form(message_type, user)

    if form.validate_on_submit():
        create_new_message(form, user, message_type)
        return redirect(url_for('.index'))

    return render_template('message.html', form=form, message_type=message_type,
                           message_url=url_for('.new_message', message_type=message_type), is_new=True)


@messages_bp.route('/<int:message_id>', methods=['GET', 'POST'])
@AuthService.auth_required
def edit_message(message_id, user, user_service):
    message = user_service.get_message(message_id)

    form = message_form(message.type, user, obj=message)
    if form.validate_on_submit():
        with db_transaction():
            form.populate_obj(message)
        return redirect(url_for('.index'))

    return render_template('message.html', form=form, message_type='datetime',
                           message_url=url_for('.edit_message', message_id=message_id), is_new=False)


def message_form(message_type, user, obj=None, data=None):
    if message_type == 'datetime':
        return DateTimeMessageForm(obj=obj, data=data)
    if message_type == 'text':
        return MessageForm(obj=obj, data=data)
    if message_type == 'task':
        form = TaskMessageForm(obj=obj, data=data)
        form.task.choices = [(t.id, t.name) for t in user.tasks]
        return form


def create_new_message(form, user, message_type):
    if message_type == 'datetime':
        new_datetime_message(form, user)
    if message_type == 'text':
        new_text_message(form, user)
    if message_type == 'task':
        new_task_message(form, user)


def new_text_message(form, user):
    UserService(user).add_message(form.text.data)


def new_datetime_message(form, user):
    UserService(user).add_datetime_message(
        form.text.data,
        form.dateformat.data,
        form.timezone.data
    )


def new_task_message(form, user):
    UserService(user).add_task_message(form.task.data, form.text.data)
