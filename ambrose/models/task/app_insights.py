from typing import Mapping, Any

from ambrose.models import db
from .task import Task


class ApplicationInsightsMetricTask(Task):
    __tablename__ = 'application_insight_metric'
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), primary_key=True)

    metric = db.Column(db.String)
    nickname = db.Column(db.String)

    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)

    aggregation = db.Column(db.String)
    timespan = db.Column(db.String)

    @property
    def type(self) -> str:
        return 'Application Insights metric'

    @property
    def name(self) -> str:
        return self.nickname if self.nickname else self.metric

    __mapper_args__ = {
        'polymorphic_identity': 'application_insight_metric',
    }

    @classmethod
    def choices(cls):
        return [
            ('requests/count', 'Request count'),
            ('requests/duration', 'Request duration'),
            ('requests/failed', 'Failed requests')
        ]

    def update(self, data: Mapping[str, Any]):
        super().update(data)
        self.metric = data.get('metric', self.metric)
        self.nickname = data.get('nickname', self.nickname)
        self.aggregation = data.get('aggregation', self.aggregation)
        self.timespan = data.get('timespan', self.timespan)