from datetime import datetime

from . import db


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    _type = db.Column(db.String)
    text = db.Column(db.String)

    @property
    def value(self):
        return self.text

    def __str__(self):
        return self.value

    __mapper_args__ = {
        'polymorphic_identity': 'message',
        'polymorphic_on': _type
    }

class TextMessage(Message):
    __tablename__ = 'text_message'

    __mapper_args__ = {
        'polymorphic_identity': 'text_message',
    }

class DateTimeMessage(Message):
    __tablename__ = 'datetime_message'

    default_format = '%b %d at %H%M'

    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), primary_key=True)
    dateformat = db.Column(db.String, default=default_format)

    @property
    def value(self):
        now = datetime.now()
        return self.text.format(now.strftime(self.dateformat))

    __mapper_args__ = {
        'polymorphic_identity': 'datetime_message',
    }


class TaskMessage(Message):
    __tablename__ = 'task_message'

    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))

    task = db.relationship('Task', uselist=False)

    @property
    def value(self):
        if self.task is None:
            return 'Invalid'

        return self.text.format(self.task.value)

    __mapper_args__ = {
        'polymorphic_identity': 'task_message',
    }