from flask import Blueprint, render_template, redirect, url_for, abort, request

from devops_monitor.common import cipher_required
from devops_monitor.models import DevOpsAccount, ApplicationInsightsAccount
from devops_monitor.services import DevOpsAccountService, UnauthorizedAccessException, AuthService
from devops_monitor.services.accounts import ApplicationInsightsAccountService, AccountService
from devops_monitor.web import DevOpsAccountForm
from devops_monitor.web.forms import NewAccountForm, ApplicationInsightsAccountForm, ApplicationInsightsMetricForm

accounts_bp = Blueprint('accounts', __name__, template_folder='templates/accounts')


@accounts_bp.route('/', methods=['GET', 'POST'])
@AuthService.auth_required
def index(user):
    form = NewAccountForm()

    form.type.choices = [
        ('devops', 'Azure DevOps'),
        ('application_insights', 'Application Insights')
    ]

    if form.validate_on_submit():
        account_type = form.type.data
        return redirect(url_for('.new_account', account_type=account_type))

    return render_template('accounts.html', new_account_form=form, accounts=user.accounts)


@accounts_bp.route('/<account_type>', methods=['GET', 'POST'])
@AuthService.auth_required
@cipher_required
def new_account(account_type, user, cipher):
    form = new_account_form(account_type)

    if form.validate_on_submit():
        create_new_account(form, user, cipher, account_type)
        return redirect(url_for('.index'))

    display_account_type = account_type.replace('_', ' ').capitalize()
    return render_template('new_account.html', form=form, account_type=display_account_type,
                           account_url=url_for('.new_account', account_type=account_type))


def new_account_form(account_type):
    if account_type == 'devops':
        return DevOpsAccountForm()
    if account_type == 'application_insights':
        return ApplicationInsightsAccountForm()

    abort(404)


def create_new_account(form, user, cipher, account_type):
    if account_type == 'devops':
        new_devops_account(form, user, cipher)
    elif account_type == 'application_insights':
        new_app_insights_account(form, user, cipher)


def new_devops_account(form, user, cipher):
    DevOpsAccountService(None, cipher).new_account(
        user,
        form.username.data,
        form.organization.data,
        form.token.data,
        form.nickname.data
    )


def new_app_insights_account(form, user, cipher):
    ApplicationInsightsAccountService(None, cipher) \
        .new_account(user, form.application_id.data, form.api_key.data)


@accounts_bp.route('/accounts/<account_id>/tasks', methods=['GET', 'POST'])
@AuthService.auth_required
@cipher_required
def account_tasks(account_id, user, cipher):
    account = None
    try:
        account = AccountService.get_account(account_id, user)
    except UnauthorizedAccessException:
        abort(403)

    if isinstance(account, DevOpsAccount):
        return devops_account_tasks(account, cipher)

    if isinstance(account, ApplicationInsightsAccount):
        return app_insights_account_tasks(account)


def devops_account_tasks(account, cipher):
    account_service = DevOpsAccountService(account, cipher)
    if request.method == 'POST':
        # TODO: WTForms to clean this up (somehow)
        task_data = {task: dict() for task in [key for key, val in request.form.items() if val == 'on']}

        for task in task_data:
            raw_properties = [val for val in request.form if val.startswith(task + '_')]
            task_data[task] = {prop.split('_', maxsplit=1)[1]: request.form[prop] for prop in raw_properties}

        account_service.update_tasks(task_data)

        return redirect(url_for('.index'))

    current_build_tasks = account_service.build_tasks
    current_release_tasks = account_service.release_tasks
    tasks = account_service.list_all_tasks()

    current_tasks = current_build_tasks.union(current_release_tasks)
    return render_template('devops_account_tasks.html', tasks=tasks, current_tasks=current_tasks, account_id=account.id)


def app_insights_account_tasks(account):
    new_metric_form = ApplicationInsightsMetricForm()
    new_metric_form.metric.choices = [
        ('requests/count', 'Request count'),
        ('requests/duration', 'Request duration'),
        ('requests/failed', 'Failed requests')
    ]

    if new_metric_form.validate_on_submit():
        ApplicationInsightsAccountService(account).add_metric(
            new_metric_form.metric.data,
            new_metric_form.nickname.data
        )

        return redirect(url_for('.index'))

    return render_template('app_insights_account_tasks.html', form=new_metric_form, account_id=account.id)
