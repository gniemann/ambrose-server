from flask import Blueprint, render_template, url_for, redirect

from devops_monitor.services import UserService
from devops_monitor.web.forms import NewMessageForm, DateTimeMessageForm, MessageForm, TaskMessageForm

messages_bp = Blueprint('messages', __name__, template_folder='templates/messages')


@messages_bp.route('/', methods=['GET', 'POST'])
@UserService.auth_required
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


@messages_bp.route('/<message_type>', methods=['GET', 'POST'])
@UserService.auth_required
def new_message(message_type, user):
    form = new_message_form(message_type, user)

    if form.validate_on_submit():
        create_new_message(form, user, message_type)
        return redirect(url_for('.index'))

    return render_template('new_message.html', form=form, message_type=message_type,
                           message_url=url_for('.new_message', message_type=message_type))


def new_message_form(message_type, user):
    if message_type == 'datetime':
        return DateTimeMessageForm()
    if message_type == 'text':
        return MessageForm()
    if message_type == 'task':
        form = TaskMessageForm()
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
    UserService.add_message(user, form.message.data)


def new_datetime_message(form, user):
    UserService.add_datetime_message(
        user,
        form.message.data,
        form.dateformat.data,
        form.timezone.data
    )


def new_task_message(form, user):
    UserService.add_task_message(user, form.task.data, form.message.data)