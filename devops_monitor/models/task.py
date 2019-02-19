from datetime import datetime

from . import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))

    user = db.relationship('User', uselist=False)
    account = db.relationship('Account', uselist=False, back_populates='tasks')

    _type = db.Column(db.String)
    _value = db.Column(db.String)
    _prev_value = db.Column(db.String)
    last_update = db.Column(db.DateTime)

    @classmethod
    def by_id(cls, task_id):
        return cls.query.get(task_id)

    @property
    def type(self):
        return self.__class__.__name__

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._prev_value = self._value
        self._value = new_value

    @property
    def has_changed(self):
        return self._prev_value != self._value

    __mapper_args__ = {
        'polymorphic_identity': 'task',
        'polymorphic_on': _type
    }

class StatusTask:
    @property
    def status(self):
        return self.value

    @status.setter
    def status(self, new_status):
        self.value = new_status

class DevOpsTask:
    project = db.Column(db.String)
    definition_id = db.Column(db.Integer)
    pipeline = db.Column(db.String)


class DevOpsBuildPipeline(Task, DevOpsTask, StatusTask):
    __tablename__ = 'devops_build_pipeline'
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), primary_key=True)

    branch = db.Column(db.String, default='master')

    @property
    def name(self):
        return self.pipeline

    @property
    def type(self):
        return 'Azure DevOps Build Pipeline'

    __mapper_args__ = {
        'polymorphic_identity': 'devops_build_pipeline',
    }

    def __eq__(self, other):
        if not hasattr(other, 'project') or \
                not hasattr(other, 'definition_id'):
            return False

        return self.project == other.project and \
            self.definition_id == other.definition_id


class DevOpsReleaseEnvironment(Task, DevOpsTask, StatusTask):
    __tablename__ = 'devops_release_environment'

    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), primary_key=True)

    environment = db.Column(db.String)
    environment_id = db.Column(db.Integer)

    @property
    def name(self):
        return '{} {}'.format(self.pipeline, self.environment)

    @property
    def type(self):
        return 'Azure DevOps Release Pipeline Environment'

    __mapper_args__ = {
        'polymorphic_identity': 'devops_release_environment',
    }

    def __eq__(self, other):
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
    def type(self):
        return 'Application Insights metric'

    @property
    def name(self):
        return self.nickname if self.nickname else self.metric

    __mapper_args__ = {
        'polymorphic_identity': 'application_insight_metric',
    }