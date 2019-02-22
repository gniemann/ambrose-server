from __future__ import annotations

from typing import Optional, Any, List, Tuple

from . import db


class Task(db.Model):
    _registry = {}
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))

    user = db.relationship('User', uselist=False)
    account = db.relationship('Account', uselist=False, back_populates='tasks')

    _type = db.Column(db.String)
    _value = db.Column(db.String)
    _prev_value = db.Column(db.String)
    last_update = db.Column(db.DateTime)
    has_changed = db.Column(db.Boolean)

    def __init_subclass__(cls, **kwargs):
        idx = cls.__name__.index('Task')
        cls._registry[cls.__name__[:idx].lower] = cls

    @classmethod
    def descriptions(cls) -> List[Tuple[str, str]]:
        return [(key, val.description) for key, val in cls._registry.items()]

    @classmethod
    def by_id(cls, task_id: int) -> Optional[Task]:
        return cls.query.get(task_id)

    @property
    def type(self) -> str:
        return self.__class__.__name__

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, new_value: str):
        self.has_changed = new_value != self._value
        if self.has_changed:
            self._prev_value = self._value
            self._value = new_value

    @property
    def prev_value(self) -> str:
        return self._prev_value

    __mapper_args__ = {
        'polymorphic_identity': 'task',
        'polymorphic_on': _type
    }


class StatusTask:
    @property
    def status(self) -> str:
        return self.value

    @status.setter
    def status(self, new_status: str):
        self.value = new_status


class DevOpsTask:
    project = db.Column(db.String)
    definition_id = db.Column(db.Integer)
    pipeline = db.Column(db.String)


class DevOpsBuildTask(Task, DevOpsTask, StatusTask):
    __tablename__ = 'devops_build_pipeline'
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), primary_key=True)

    branch = db.Column(db.String, default='master')

    @property
    def name(self) -> str:
        return self.pipeline

    @property
    def type(self) -> str:
        return 'Azure DevOps Build Pipeline'

    __mapper_args__ = {
        'polymorphic_identity': 'devops_build_pipeline',
    }

    def __eq__(self, other: Any) -> bool:
        if not hasattr(other, 'project') or \
                not hasattr(other, 'definition_id'):
            return False

        return self.project == other.project and \
               self.definition_id == other.definition_id


class DevOpsReleaseTask(Task, DevOpsTask, StatusTask):
    __tablename__ = 'devops_release_environment'

    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), primary_key=True)

    environment = db.Column(db.String)
    environment_id = db.Column(db.Integer)

    @property
    def name(self) -> str:
        return '{} {}'.format(self.pipeline, self.environment)

    @property
    def type(self) -> str:
        return 'Azure DevOps Release Pipeline Environment'

    __mapper_args__ = {
        'polymorphic_identity': 'devops_release_environment',
    }

    def __eq__(self, other: Any) -> bool:
        if not hasattr(other, 'project') or \
                not hasattr(other, 'definition_id') or \
                not hasattr(other, 'environment_id'):
            return False

        return self.project == other.project and \
               self.definition_id == other.definition_id and \
               self.environment_id == other.environment_id


class ApplicationInsightMetricTask(Task):
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
