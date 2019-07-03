from concurrent import futures

import celery
from cryptography.fernet import Fernet
from flask import current_app

from ambrose.models import Account
from ambrose.services import AccountService

celery_app = celery.Celery()

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60, update_accounts.s(), name="update tasks")


@celery_app.task
def update_accounts():
    print("Updating all accounts")
    cipher = Fernet(current_app.secret_key)

    jobs = []
    # with futures.ThreadPoolExecutor() as executor:
    for account in Account.all():
        service = AccountService(account, cipher)
        service.get_task_statuses()
            # jobs.append(executor.submit(service.get_task_statuses))

    # futures.wait(jobs)