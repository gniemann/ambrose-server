from cryptography.fernet import Fernet
from flask import Blueprint, render_template, redirect, url_for, abort

from ambrose.common import cipher_required
from ambrose.models import User, GitHubAccount, ApplicationInsightsAccount, DevOpsAccount
from ambrose.services import DevOpsAccountService, UnauthorizedAccessException, AuthService, \
    ApplicationInsightsAccountService, GitHubAccountService, AccountService
from .forms import NewAccountForm, ApplicationInsightsMetricForm, AccountForm, GitHubRepoStatusForm, \
    DevOpsTaskForm

accounts_bp = Blueprint('accounts', __name__, template_folder='templates/accounts')


@accounts_bp.route('/', methods=['GET', 'POST'])
@AuthService.auth_required
def index(user: User):
    form = NewAccountForm()

    if form.validate_on_submit():
        account_type = form.type.data
        return redirect(url_for('.new_account', account_type=account_type))

    return render_template('accounts.html', new_account_form=form, accounts=user.accounts)


@accounts_bp.route('/<account_type>', methods=['GET', 'POST'])
@AuthService.auth_required
@cipher_required
def new_account(account_type: str, user: User, cipher: Fernet):
    form = AccountForm.new_account_form(account_type)

    if form.validate_on_submit():
        data = form.data
        data.pop('csrf_token', None)

        AccountService.create_account(account_type, cipher, user, **data)
        return redirect(url_for('.index'))

    display_account_type = account_type.replace('_', ' ').capitalize()
    return render_template('new_account.html', form=form, account_type=display_account_type,
                           account_url=url_for('.new_account', account_type=account_type))


@accounts_bp.route('/<int:account_id>', methods=['GET', 'POST'])
@AuthService.auth_required
@cipher_required
def account(account_id: int, user: User, cipher: Fernet):
    account = None
    try:
        account = AccountService.get_account(account_id, user)
    except UnauthorizedAccessException:
        abort(403)

    form = AccountForm.edit_account_form(account)

    if form.validate_on_submit():
        data = form.data
        data.pop('csrf_token', None)
        AccountService(account, cipher).edit_account(**data)

        return redirect(url_for('.index'))

    return render_template('edit_account.html', form=form, account_id=account_id)


@accounts_bp.route('/<int:account_id>/tasks', methods=['GET', 'POST'])
@AuthService.auth_required
@cipher_required
def account_tasks(account_id: int, user: User, cipher: Fernet):
    account = None
    try:
        account = AccountService.get_account(account_id, user)
    except UnauthorizedAccessException:
        abort(403)

    if isinstance(account, DevOpsAccount):
        return devops_account_tasks(account, cipher)

    if isinstance(account, ApplicationInsightsAccount):
        return app_insights_account_tasks(account)

    if isinstance(account, GitHubAccount):
        return github_account_tasks(account, cipher)


def devops_account_tasks(account: DevOpsAccount, cipher: Fernet):
    account_service = DevOpsAccountService(account, cipher)
    task_form = DevOpsTaskForm()
    if task_form.validate_on_submit():
        account_service.update_build_tasks(t for t in task_form.builds.data if t['monitored'])
        account_service.update_release_tasks(t for t in task_form.releases.data if t['monitored'])

        return redirect(url_for('.index'))

    current_build_tasks = account_service.build_tasks
    current_release_tasks = account_service.release_tasks
    tasks = account_service.list_all_tasks()
    for t in current_release_tasks:
        for other in (task for task in tasks if task.type == 'release'):
            if other == t:
                other.uses_webhook = t.uses_webhook

    task_form = DevOpsTaskForm.build(tasks, current_build_tasks, current_release_tasks)
    return render_template('devops_account_tasks.html', account_id=account.id, form=task_form)


def app_insights_account_tasks(account: ApplicationInsightsAccount):
    new_metric_form = ApplicationInsightsMetricForm()

    if new_metric_form.validate_on_submit():
        ApplicationInsightsAccountService(account).add_metric(
            new_metric_form.metric.data,
            new_metric_form.nickname.data,
            new_metric_form.aggregation.data,
            new_metric_form.timespan.data
        )

        return redirect(url_for('.index'))

    return render_template('app_insights_account_tasks.html', form=new_metric_form, account_id=account.id)


def github_account_tasks(account: GitHubAccount, cipher: Fernet):
    form = GitHubRepoStatusForm()

    if form.validate_on_submit():
        GitHubAccountService(account, cipher).add_repo_task(form.repo.data, form.nickname.data)

        return redirect(url_for('.index'))

    return render_template('github_account_tasks.html', form=form, account_id=account.id)
