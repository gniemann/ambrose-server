from __future__ import annotations

from typing import List, Tuple, Optional

from ambrose.models import db
from ambrose.models.task import Task


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
    def descriptions(cls) -> List[Tuple[str, str]]:
        return [(key, val.description) for key, val in cls._registry.items()]

    @classmethod
    def by_id(cls, account_id: int) -> Optional[Account]:
        return cls.query.get(account_id)

    @classmethod
    def all(cls) -> List[Account]:
        return cls.query.all()

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