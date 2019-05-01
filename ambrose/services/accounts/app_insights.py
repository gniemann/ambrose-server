import itertools
from datetime import datetime

from ambrose.common import db_transaction
from ambrose.models import ApplicationInsightsAccount, ApplicationInsightsMetricTask
from .account_service import AccountService
from application_insights import ApplicationInsightsService


class ApplicationInsightsAccountService(AccountService, model=ApplicationInsightsAccount):
    def _new_account(self, application_id: str, api_key: str, nickname: str) -> ApplicationInsightsAccount:
        return ApplicationInsightsAccount(
            application_id=application_id,
            api_key=self._encrypt(api_key),
            nickname=nickname
        )

    def edit_account(self, application_id: str, api_key: str, nickname: str):
        with db_transaction():
            self.account.application_id = application_id
            self.account.nickname = nickname

            if len([c for c in api_key if c != '*']) > 0:
                self.account.api_key = self._encrypt(api_key)

    def add_metric(self, metric: str, nickname: str, aggregation: str, timespan: str):
        with db_transaction():
            self.account.add_task(ApplicationInsightsMetricTask(
                metric=metric,
                nickname=nickname,
                aggregation=aggregation,
                timespan=timespan
            ))

    def get_task_statuses(self):
        insights = ApplicationInsightsService(self.account.application_id, self._decrypt(self.account.api_key))
        with db_transaction():
            for task in [t for t in self.account.tasks if isinstance(t, ApplicationInsightsMetricTask)]:
                metric = insights.get_metric(task.metric, aggregation=task.aggregation, timespan=task.timespan)
                if metric:
                    task.last_update = datetime.now()
                    task.value = metric.value
                    task.start = metric.start
                    task.end = metric.end