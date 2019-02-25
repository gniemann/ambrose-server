from __future__ import annotations

from datetime import datetime
from typing import Tuple, Optional, Mapping, Any

import dateutil

from . import db


class Message(db.Model):
    _registry = {}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    _type = db.Column(db.String)
    text = db.Column(db.String)

    def __init_subclass__(cls, **kwargs):
        idx = cls.__name__.index('Message')
        cls._registry[cls.__name__[:idx].lower()] = cls

    @classmethod
    def new_message(cls, message_type: str, data: Mapping[str, Any] = None) -> Message:
        msg = cls._registry[message_type.lower()]()
        if data:
            msg.update(data)

        return msg

    @classmethod
    def message_descriptions(cls) -> [Tuple[str, str]]:
        return [(key, val.description) for key, val in cls._registry.items()]

    @property
    def value(self) -> str:
        return self.text.format(**self._substitutions())

    def __str__(self):
        return self.value

    @classmethod
    def by_id(cls, message_id: int) -> Optional[Message]:
        return cls.query.get(message_id)

    @property
    def type(self) -> str:
        return self._type.split('_')[0]

    __mapper_args__ = {
        'polymorphic_identity': 'message',
        'polymorphic_on': _type
    }

    def update(self, data: Mapping[str, Any]):
        new_text = data.get('text')
        if new_text is not None:
            self.text = self._sanatize_text(new_text)

    def _sanatize_text(self, text: str) -> str:
        default = ''
        sub_vars = self.class_variables()
        if len(sub_vars) > 0:
            default = sub_vars[0]

        return text.replace('{}', '{' + default + '}')

    @classmethod
    def class_variables(cls):
        return []

    @property
    def variables(self):
        return self.class_variables()

    def _substitutions(self):
        return {var: getattr(self, var) for var in self.variables}

    @classmethod
    def class_variables_for(cls, message_type):
        return cls._registry[message_type.lower()].class_variables()

class TextMessage(Message):
    __tablename__ = 'text_message'

    __mapper_args__ = {
        'polymorphic_identity': 'text_message',
    }

    description = "Static text"


class DateTimeMessage(Message):
    __tablename__ = 'datetime_message'

    description = "Datetime"

    default_format = '%b %d at %H%M'

    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), primary_key=True)
    dateformat = db.Column(db.String, default=default_format)
    timezone = db.Column(db.String)

    __mapper_args__ = {
        'polymorphic_identity': 'datetime_message',
    }

    def update(self, data: Mapping[str, Any]):
        super(DateTimeMessage, self).update(data)
        self.dateformat = data.get('dateformat', self.dateformat)

    @classmethod
    def class_variables(cls):
        return super().class_variables() + ['datetime']

    def _substitutions(self):
        tz = dateutil.tz.gettz(self.timezone)
        now = datetime.now(tz=tz)
        return {
            'datetime': now.strftime(self.dateformat)
        }


class TaskMessage(Message):
    __tablename__ = 'task_message'

    description = "Task status"

    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))

    task = db.relationship('Task', uselist=False)

    @property
    def value(self) -> str:
        if self.task is None:
            return 'Invalid'

        return super().value

    __mapper_args__ = {
        'polymorphic_identity': 'task_message',
    }

    _task_variables = ['value', 'name', 'prev_value', 'has_changed', 'last_update']

    def update(self, data: Mapping[str, Any]):
        super(TaskMessage, self).update(data)
        self.task_id = data.get('task_id', self.task_id)

    @classmethod
    def class_variables(cls):
        return super().class_variables() + cls._task_variables

    def _substitutions(self):
        return {var: getattr(self.task, var) for var in self._task_variables}