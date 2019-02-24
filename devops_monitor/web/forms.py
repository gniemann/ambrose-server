from __future__ import annotations

import pytz
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FormField, FieldList, HiddenField, SelectField, IntegerField
from wtforms.validators import InputRequired, EqualTo

from devops_monitor.models import Message, Account, ApplicationInsightsMetricTask


class LoginForm(FlaskForm):
    username = StringField('Username', [InputRequired()], render_kw={'required': True})
    password = PasswordField('Password', [InputRequired()], render_kw={'required': True})


class RegisterForm(FlaskForm):
    username = StringField('Username', [InputRequired()], render_kw={'required': True})
    password = PasswordField('Password', [InputRequired(), EqualTo('confirm_password', message='Passwords did not match')], render_kw={'required': True})
    confirm_password = PasswordField('Confirm Password', render_kw={'required': True})


class NewAccountForm(FlaskForm):
    type = SelectField('Select new account type')

    def __init__(self, *args, **kwargs):
        super(NewAccountForm, self).__init__(*args, **kwargs)
        self.type.choices = Account.descriptions()


class AccountForm(FlaskForm):
    _register = {}

    def __init_subclass__(cls, **kwargs):
        idx = cls.__name__.index('AccountForm')
        cls._register[cls.__name__[:idx].lower()] = cls

    @classmethod
    def new_account_form(cls, account_type: str, *args, **kwargs) -> NewAccountForm:
        form_type = cls._register[account_type.lower()]
        return form_type(*args, **kwargs)


class DevOpsAccountForm(AccountForm):
    username = StringField('Username', [InputRequired()], render_kw={'required': True})
    organization = StringField('Organization', [InputRequired()], render_kw={'required': True})
    token = StringField('DevOps Personal Access Token', [InputRequired()], render_kw={'required': True})
    nickname = StringField('Nickname')


class ApplicationInsightsAccountForm(AccountForm):
    application_id = StringField('Application ID', [InputRequired()], render_kw={'required': True})
    api_key = StringField('API Key', [InputRequired()], render_kw={'required': True})


def create_edit_form(lights, tasks):
    task_choices = [(t.id, t.name) for t in tasks]
    task_choices.insert(0, (-1, 'None'))

    class LightForm(FlaskForm):
        class Meta(FlaskForm.Meta):
            csrf = False

        slot = HiddenField()
        task = SelectField(choices=task_choices, coerce=int)

    light_cnt = len(lights)

    class EditForm(FlaskForm):
        num_lights = IntegerField('Number of lights')
        lights = FieldList(FormField(LightForm), min_entries=light_cnt)

    light_data = []
    for light in lights:
        task_id = light.task.id if light.task else -1
        light_data.append({
            'slot': light.slot,
            'task': task_id
        })

    data = {
        'lights': light_data,
        'num_lights': light_cnt
    }

    return EditForm(data=data)


class NewTaskForm(FlaskForm):
    account = SelectField('Select account', coerce=int)


class ApplicationInsightsMetricForm(FlaskForm):
    metric = SelectField('Select metric')
    aggregation = SelectField("Select aggregation", choices=[('avg', 'Average'), ('sum', 'Sum'), ('min', 'Min'), ('max', 'Max'), ('count', 'Count')])
    timespan = StringField('Timespan')
    nickname = StringField('Nickname')

    def __init__(self, *args, **kwargs):
        super(ApplicationInsightsMetricForm, self).__init__(*args, **kwargs)
        self.metric.choices = ApplicationInsightsMetricTask.choices()


class NewMessageForm(FlaskForm):
    type = SelectField('Select task type')

    def __init__(self, *args, **kwargs):
        super(NewMessageForm, self).__init__(*args, **kwargs)
        self.type.choices = Message.message_descriptions()


class MessageForm(FlaskForm):
    _registry = {}

    def __init_subclass__(cls, **kwargs):
        idx = cls.__name__.index('MessageForm')
        cls._registry[cls.__name__[:idx].lower()] = cls

    @classmethod
    def new_message_form(cls, message_type, *args, **kwargs):
        form_type = cls._registry[message_type.lower()]
        return form_type(*args, **kwargs)

    text = StringField('Enter message', render_kw={'required': True})


class TextMessageForm(MessageForm):
    pass


class DateTimeMessageForm(MessageForm):
    dateformat = StringField('Enter datetime format')
    timezone = SelectField('Select display timezone', choices=[(tz, tz) for tz in pytz.all_timezones if tz.startswith('US')])


class TaskMessageForm(MessageForm):
    task_id = SelectField('Select task', coerce=int)

    def __init__(self, *args, user, **kwargs):
        super(TaskMessageForm, self).__init__(*args, **kwargs)
        self.task_id.choices = [(t.id, t.name) for t in user.tasks]