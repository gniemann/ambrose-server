from datetime import datetime

import requests

from ambrose.models import WebAccount, HealthcheckTask
from ambrose.common import db_transaction
from . import AccountService


class WebAccountService(AccountService, model=WebAccount):
    def _new_account(self, base_url: str, nickname: str) -> WebAccount:
        return WebAccount(base_url=base_url, nickname=nickname)

    def add_healthcheck(self, path: str):
        with db_transaction():
            self.account.add_task(HealthcheckTask(path=path))

    def get_task_statuses(self):
        for task in self.account.tasks:
            if isinstance(task, HealthcheckTask):
                url = self.account.base_url + task.path
                res = requests.get(url)

                with db_transaction():
                    if 200 <= res.status_code < 400:
                        task.status = "healthy"
                    else:
                        task.status = "not-healthy"
                    task.last_update = datetime.now()