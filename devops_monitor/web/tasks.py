from flask import Blueprint, render_template, redirect, url_for

from devops_monitor.services import UserService
from devops_monitor.web.forms import DateTimeMessageForm, NewTaskForm

tasks_bp = Blueprint('tasks', __name__, template_folder='templates/tasks')

@tasks_bp.route('/', methods=['GET', 'POST'])
@UserService.auth_required
def index(user):
    new_task_form = NewTaskForm()

    if new_task_form.validate_on_submit():
        return redirect(url_for('.datetime_message'))

    return render_template('tasks.html', tasks=user.tasks, form=new_task_form)


@tasks_bp.route('/datetime_message', methods=['GET', 'POST'])
@UserService.auth_required
def datetime_message(user):
    message_form = DateTimeMessageForm()

    if message_form.validate_on_submit():
        UserService.add_datetime_message(user, message_form.message.data, message_form.dateformat.data)

        return redirect(url_for('.index'))

    return render_template('date_time_task.html', form=message_form)

