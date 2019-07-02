from typing import Any, Mapping

from ambrose.models import db
from .task import Task, StatusTask


class HealthcheckTask(Task, StatusTask):
    __tablename__ = 'healthcheck_task'
    __mapper_args__ = {
        'polymorphic_identity': 'healthcheck_task'
    }

    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), primary_key=True)

    path = db.Column(db.String)

    @property
    def type(self) -> str:
        return 'Healthcheck'

    @property
    def name(self) -> str:
        return 'Healthcheck for {}'.format(self.account.base_url)

    def update(self, data: Mapping[str, Any]):
        super().update(data)
        self.url = data.get('url', self.url)
