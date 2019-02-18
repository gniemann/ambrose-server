from flask import Blueprint, render_template, redirect, url_for, abort, request

from devops_monitor.common import cipher_required
from devops_monitor.models import DevOpsAccount, ApplicationInsightsAccount
from devops_monitor.services import UserService, DevOpsAccountService, UnauthorizedAccessException
from devops_monitor.services.accounts import ApplicationInsightsAccountService, AccountService
from devops_monitor.web import DevOpsAccountForm
from devops_monitor.web.forms import NewAccountForm, ApplicationInsightsAccountForm, ApplicationInsightsMetricForm

accounts_bp = Blueprint('accounts', __name__, template_folder='templates/accounts')

@accounts_bp.route('/accounts', methods=['GET', 'POST'])
@UserService.auth_required
def index(user):
    new_account_form = NewAccountForm()

    new_account_form.type.choices = [(0, 'Azure DevOps'), (1, 'Application Insights')]
    if new_account_form.validate_on_submit():
        type_index = new_account_form.type.data
        if type_index == 0:
            return redirect(url_for('.devops_account'))
        if type_index == 1:
            return redirect(url_for('.app_insights_account'))

    return render_template('accounts.html', new_account_form=new_account_form, accounts=user.accounts)


@accounts_bp.route('/devops_account', methods=['GET', 'POST'])
@UserService.auth_required
@cipher_required
def devops_account(user, cipher):
    new_account_form = DevOpsAccountForm(data={'username': user.username})

    if new_account_form.validate_on_submit():
        DevOpsAccountService(cipher).new_account(
            user,
            new_account_form.username.data,
            new_account_form.organization.data,
            new_account_form.token.data,
            new_account_form.nickname.data
        )

        return redirect(url_for('.index'))

    return render_template('devops.html', new_account_form=new_account_form)

@accounts_bp.route('/application_insights', methods=['GET', 'POST'])
@UserService.auth_required
@cipher_required
def app_insights_account(user, cipher):
    new_account_form = ApplicationInsightsAccountForm()

    if new_account_form.validate_on_submit():
        ApplicationInsightsAccountService(cipher)\
            .new_account(user, new_account_form.application_id.data, new_account_form.api_key.data)

        return redirect(url_for('.index'))

    return render_template('application_insights.html', new_account_form=new_account_form)

@accounts_bp.route('/accounts/<account_id>/tasks', methods=['GET', 'POST'])
@UserService.auth_required
@cipher_required
def account_tasks(account_id, user, cipher):
    account = None
    try:
        account = AccountService().get_account(account_id, user)
    except UnauthorizedAccessException:
        abort(403)

    if isinstance(account, DevOpsAccount):
        return devops_account_tasks(account, cipher)

    if isinstance(account, ApplicationInsightsAccount):
        return app_insights_account_tasks(account)

def devops_account_tasks(account, cipher):
    account_service = DevOpsAccountService(cipher)
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
    return render_template('devops_account_tasks.html', tasks=tasks, current_tasks=current_tasks, account_id=account.id)

def app_insights_account_tasks(account):
    new_metric_form = ApplicationInsightsMetricForm()
    new_metric_form.metric.choices = [('requests/count', 'Request count')]

    if new_metric_form.validate_on_submit():
        ApplicationInsightsAccountService().add_metric(
            account,
            new_metric_form.metric.data,
            new_metric_form.nickname.data
        )

        return redirect(url_for('.index'))

    return render_template('app_insights_account_tasks.html', form=new_metric_form, account_id=account.id)
