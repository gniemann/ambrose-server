import pytz
from flask_wtf import FlaskForm
from wtforms import SelectField, FieldList, StringField

from ambrose.models import Message


class NewMessageForm(FlaskForm):
    type = SelectField('Select task type')

    def __init__(self, *args, **kwargs):
        super(NewMessageForm, self).__init__(*args, **kwargs)
        self.type.choices = Message.message_descriptions()


class MessageForm(FlaskForm):
    """
    Base class for message edit/creation forms. This class maintains a registry of its subclasses and
    provides an abstract factory method for generating them.
    """
    _registry = {}

    def __init_subclass__(cls, **kwargs):
        idx = cls.__name__.index('MessageForm')
        cls._registry[cls.__name__[:idx].lower()] = cls

    @classmethod
    def new_message_form(cls, message_type: str, *args, **kwargs):
        """
        Abstract factory method for creating MessageForms based on a type
        :param message_type: A string describing the message
        :return: A MessageForm for the required type
        """
        form_type = cls._registry[message_type.lower()]
        return form_type(*args, **kwargs)

    nickname = StringField('Nickname')
    text = StringField('Enter message', render_kw={'required': True})


class TextMessageForm(MessageForm):
    pass


class DateTimeMessageForm(MessageForm):
    dateformat = StringField('Enter datetime format')
    timezone = SelectField('Select display timezone',
                           choices=[(tz, tz) for tz in pytz.all_timezones if tz.startswith('US')])


class TaskMessageForm(MessageForm):
    task_id = SelectField('Select task', coerce=int)

    def __init__(self, *args, user, **kwargs):
        super(TaskMessageForm, self).__init__(*args, **kwargs)
        self.task_id.choices = [(t.id, t.name) for t in user.tasks]


class RandomMessageForm(MessageForm):
    messages = FieldList(StringField('Text'), 'Random Messages', min_entries=10)
