from __future__ import annotations

from typing import List, Tuple, Optional, Mapping, Any

from ambrose.models import db


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
    uses_webhook = db.Column(db.Boolean, default=False)

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
        if new_value != self._value:
            self.has_changed = True
            self._prev_value = self._value
            self._value = new_value

    @property
    def prev_value(self) -> str:
        return self._prev_value

    __mapper_args__ = {
        'polymorphic_identity': 'task',
        'polymorphic_on': _type
    }

    def update(self, data: Mapping[str, Any]):
        pass


class StatusTask:
    @property
    def status(self) -> str:
        return self.value

    @status.setter
    def status(self, new_status: str):
        self.value = new_status
