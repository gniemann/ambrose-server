from typing import Any

from ambrose.models import db
from .task import Task, StatusTask


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