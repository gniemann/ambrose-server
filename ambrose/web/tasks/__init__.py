from flask import Blueprint, render_template, redirect, url_for

from ambrose.models import User
from ambrose.services import AuthService, UserService
from ambrose.web.forms import NewTaskForm, TaskForm

tasks_bp = Blueprint('tasks', __name__, template_folder='templates')


@tasks_bp.route('/', methods=['GET', 'POST'])
@AuthService.auth_required
def index(user: User):
    new_task_form = NewTaskForm()
    new_task_form.account.choices = [(a.id, a.name) for a in user.accounts]

    if new_task_form.validate_on_submit():
        account_id = new_task_form.account.data
        return redirect(url_for('accounts.account_tasks', account_id=account_id))

    token = AuthService.jwt(user)
    return render_template('tasks.html', tasks=user.tasks, form=new_task_form, jwt=token)


@tasks_bp.route('/<int:task_id>', methods=['GET', 'POST'])
@AuthService.auth_required
def task(task_id: int, user_service: UserService):
    task = user_service.get_task(task_id)
    form = TaskForm.form_for_task(task)

    if form.validate_on_submit():
        user_service.update_task(task, form.data)
        return redirect(url_for('.index'))

    return render_template('task.html', form=form, task_url=url_for('.task', task_id=task_id, is_new=False))