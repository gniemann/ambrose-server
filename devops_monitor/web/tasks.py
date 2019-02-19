from flask import Blueprint, render_template, redirect, url_for

from devops_monitor.services import UserService
from devops_monitor.web.forms import DateTimeMessageForm, NewTaskForm

tasks_bp = Blueprint('tasks', __name__, template_folder='templates/tasks')

@tasks_bp.route('/', methods=['GET', 'POST'])
@UserService.auth_required
def index(user):
    new_task_form = NewTaskForm()
    new_task_form.type.choices = []

    if new_task_form.validate_on_submit():
        return redirect(url_for('.index'))

    return render_template('tasks.html', tasks=user.tasks, form=new_task_form)