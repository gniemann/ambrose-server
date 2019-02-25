from flask import Blueprint, render_template, redirect, url_for

from devops_monitor.services import AuthService
from devops_monitor.web.forms import NewTaskForm

tasks_bp = Blueprint('tasks', __name__, template_folder='templates/tasks')


@tasks_bp.route('/', methods=['GET', 'POST'])
@AuthService.auth_required
def index(user):
    new_task_form = NewTaskForm()
    new_task_form.account.choices = [(a.id, a.name) for a in user.accounts]

    if new_task_form.validate_on_submit():
        account_id = new_task_form.account.data
        return redirect(url_for('accounts.account_tasks', account_id=account_id))

    token = AuthService.jwt(user)
    return render_template('tasks.html', tasks=user.tasks, form=new_task_form, jwt=token)
