import celery
from cryptography.fernet import Fernet
from flask import current_app

from devops_monitor.models import Account
from devops_monitor.services import AccountService

celery_app = celery.Celery()

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60, update_accounts.s(), name="update tasks")


@celery_app.task
def update_accounts():
    print("Updating all accounts")
    cipher = Fernet(current_app.secret_key)
    for account in Account.all():
        AccountService(account, cipher).get_task_statuses()
