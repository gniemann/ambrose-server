from typing import Any, List

from ambrose.models import db
from ambrose.models.task import Task, DevOpsBuildTask, DevOpsReleaseTask
from .account import Account


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
    def build_tasks(self) -> List[DevOpsBuildTask]:
        return [t for t in self.tasks if isinstance(t, DevOpsBuildTask)]

    @property
    def release_tasks(self) -> List[DevOpsReleaseTask]:
        return [t for t in self.tasks if isinstance(t, DevOpsReleaseTask)]