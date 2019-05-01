from typing import Mapping, Any

from .task import Task, StatusTask
from ambrose.models import db

class GitHubRepositoryStatusTask(Task, StatusTask):
    __tablename__ = 'github_repoistory_status'
    __mapper_args__ = {
        'polymorphic_identity': 'github_repository_status',
    }

    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), primary_key=True)

    owner = db.Column(db.String)
    repo_name = db.Column(db.String)

    pr_count = db.Column(db.Integer)

    @classmethod
    def by_repo(cls, repo_name):
        return cls.query.filter_by(repo_name=repo_name).first()

    @property
    def repo(self):
        return '{}/{}'.format(self.owner, self.repo_name)

    def update(self, data: Mapping[str, Any]):
        super().update(data)
        self.uses_webhook = data.get('uses_webhook', self.uses_webhook)