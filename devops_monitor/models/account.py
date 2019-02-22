from __future__ import annotations
from typing import Tuple, List, Optional, Any

from . import db
from .task import Task, DevOpsReleaseEnvironment, DevOpsBuildPipeline


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    type = db.Column(db.String)
    nickname = db.Column(db.String)

    user = db.relationship('User', back_populates='accounts')
    tasks = db.relationship('Task', back_populates='account')

    __mapper_args__ = {
        'polymorphic_identity': 'account',
        'polymorphic_on': type
    }

    _registry = {}

    def __init_subclass__(cls, **kwargs):
        idx = cls.__name__.index('Account')
        cls._registry[cls.__name__[:idx].lower()] = cls

    @classmethod
    def account_descriptions(cls) -> List[Tuple[str, str]]:
        return [(key, val.description) for key, val in cls._registry.items()]

    @classmethod
    def by_id(cls, account_id: int) -> Optional[Account]:
        return cls.query.get(account_id)

    @property
    def name(self) -> str:
        return self.nickname if self.nickname else self.type

    def add_task(self, task: Task):
        if isinstance(task, Task):
            task.user_id = self.user_id
            task.account_id = self.id
            self.tasks.append(task)

    def remove_task(self, task: Task):
        if isinstance(task, Task):
            self.tasks.remove(task)


class DevOpsAccount(Account):
    __tablename__ = 'devops_account'
    description = 'Azure DevOps'

    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), primary_key=True)

    username = db.Column(db.String)
    organization = db.Column(db.String)
    token = db.Column(db.String)

    __mapper_args__ = {
        'polymorphic_identity': 'devops_account'
    }

    def remove_task(self, task: Any):
        if isinstance(task, Task):
            super(DevOpsAccount, self).remove_task(task)
        else:
            for t in self.tasks:
                if t == task:
                    self.tasks.remove(t)

    @property
    def build_tasks(self) -> List[DevOpsBuildPipeline]:
        return [t for t in self.tasks if isinstance(t, DevOpsBuildPipeline)]

    @property
    def release_tasks(self) -> List[DevOpsReleaseEnvironment]:
        return [t for t in self.tasks if isinstance(t, DevOpsReleaseEnvironment)]


class ApplicationInsightsAccount(Account):
    __tablename__ = 'application_insights_account'
    description = 'Application Insights'

    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), primary_key=True)

    application_id = db.Column(db.String)
    api_key = db.Column(db.String)

    __mapper_args__ = {
        'polymorphic_identity': 'application_insights_account'
    }
