from datetime import datetime

from . import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))

    user = db.relationship('User', uselist=False)
    account = db.relationship('Account', uselist=False, back_populates='tasks')

    _type = db.Column(db.String)
    _status = db.Column(db.String)
    prev_status = db.Column(db.String)
    has_changed = db.Column(db.Boolean)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_status):
        self.has_changed = new_status != self._status

        if self.has_changed:
            self.prev_status = self.status
            self._status = new_status

    @classmethod
    def by_id(cls, task_id):
        return cls.query.get(task_id)

    @property
    def type(self):
        return self.__class__.__name__

    @property
    def name(self):
        return self.__class__.__name__

    __mapper_args__ = {
        'polymorphic_identity': 'task',
        'polymorphic_on': _type
    }


class DevOpsTask:
    project = db.Column(db.String)
    definition_id = db.Column(db.Integer)
    pipeline = db.Column(db.String)


class DevOpsBuildPipeline(Task, DevOpsTask):
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


class DevOpsReleaseEnvironment(Task, DevOpsTask):
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


class MessageTask:
    format = db.Column(db.String)

    @property
    def message(self):
        return format


class DateTimeMessageTask(Task, MessageTask):
    __tablename__ = 'date_time_message'
    default_format = '%b %m, %M%M'
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), primary_key=True)
    dateformat = db.Column(db.String, default=default_format)

    @property
    def type(self):
        return 'DateTime Message'

    @property
    def name(self):
        return self.message

    @property
    def message(self):
        now = datetime.now()
        return self.format.format(now.strftime(self.dateformat))

    __mapper_args__ = {
        'polymorphic_identity': 'date_time_message',
    }

class MetricTask:
    value = db.Column(db.Numeric)

class ApplicationInsightMetricTask(Task):
    __tablename__ = 'application_insight_metric'
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), primary_key=True)

    metric = db.Column(db.String)
    nickname = db.Column(db.String)

    @property
    def type(self):
        return 'Application Insights metric'

    @property
    def name(self):
        return self.nickname if self.nickname else self.metric

    __mapper_args__ = {
        'polymorphic_identity': 'application_insight_metric',
    }