from __future__ import annotations

from typing import List, Iterable

import pytz
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FormField, FieldList, HiddenField, SelectField, IntegerField, \
    BooleanField
from wtforms.validators import InputRequired, EqualTo

from ambrose.models import Message, Account, ApplicationInsightsMetricTask, Task, GitHubRepositoryStatusTask, \
    StatusLight


class LoginForm(FlaskForm):
    username = StringField('Username', [InputRequired()], render_kw={'required': True})
    password = PasswordField('Password', [InputRequired()], render_kw={'required': True})


class RegisterForm(FlaskForm):
    username = StringField('Username', [InputRequired()], render_kw={'required': True})
    password = PasswordField('Password',
                             [InputRequired(), EqualTo('confirm_password', message='Passwords did not match')],
                             render_kw={'required': True})
    confirm_password = PasswordField('Confirm Password', render_kw={'required': True})


class NewAccountForm(FlaskForm):
    type = SelectField('Select new account type')

    def __init__(self, *args, **kwargs):
        super(NewAccountForm, self).__init__(*args, **kwargs)
        self.type.choices = Account.descriptions()


class AccountForm(FlaskForm):
    """
    Base class for account edit/creation form. This class keeps track of its subclasses (which must have a name
    ending in 'AccountForm') and uses that information to create the correct subclass.

    The two class methods new_account_form and edit_account_form are factory methods for creating forms.
    """
    _register = {}

    nickname = StringField('Nickname')

    def __init_subclass__(cls, **kwargs):
        idx = cls.__name__.index('AccountForm')
        cls._register[cls.__name__[:idx].lower()] = cls

    @classmethod
    def new_account_form(cls, account_type: str, *args, **kwargs) -> AccountForm:
        """
        Abstract factory method that creates an empty form for the given account_type

        :param account_type: describes the type of account, ie 'DevOps'
        :return: an appropriate subclass of AccountForm for the account_type
        """
        form_type = cls._register[account_type.lower()]
        return form_type(*args, **kwargs)

    @classmethod
    def edit_account_form(cls, account: Account, *args, **kwargs) -> AccountForm:
        """
        Abstract factory method that creates and populates a form for the given account. THe account is passed as the 'obj' parameter to the form constructor.

        :param account: The account requiring a form
        :return: An AccountForm subclass, populated with the account
        """
        idx = account.__class__.__name__.index('Account')
        account_type = account.__class__.__name__[:idx].lower()
        form_type = cls._register[account_type]
        return form_type(*args, obj=account, **kwargs)


class DevOpsAccountForm(AccountForm):
    username = StringField('Username', [InputRequired()], render_kw={'required': True})
    organization = StringField('Organization', [InputRequired()], render_kw={'required': True})
    token = StringField('DevOps Personal Access Token', [InputRequired()], render_kw={'required': True})


class ApplicationInsightsAccountForm(AccountForm):
    application_id = StringField('Application ID', [InputRequired()], render_kw={'required': True})
    api_key = StringField('API Key', [InputRequired()], render_kw={'required': True})


class GitHubAccountForm(AccountForm):
    token = StringField('Personal Access Token', [InputRequired()], render_kw={'required': True})


def create_edit_form(lights: List[StatusLight], tasks: List[Task]) -> FlaskForm:
    """
    Creates the edit light form, given a set of lights and tasks
    :param lights: An iterable of the current StatusLights
    :param tasks: An iterable of the current tasks.
    :return: An EditForm for editing the light configuration
    """
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


class TaskForm(FlaskForm):
    """
    Base class for (most) Task edit/creation forms. This class maintains a registry of its subclasses and provices an abstract factory method for generating the correct form given a task.
    """
    _model_registry = {}
    nickname = StringField('Nickname')

    def __init_subclass__(cls, **kwargs):
        cls._model_registry[cls._model.__name__] = cls

    @classmethod
    def form_for_task(cls, task, *args, **kwargs):
        """
        Abstract factory method for creating the correct TaskForm subclass for a given task.

        :param task: The task requiring a form
        :return: A TaskForm subvlass, populated with the data from task
        """
        form_type = cls._model_registry.get(task.__class__.__name__, cls)
        return form_type(*args, obj=task, **kwargs)


class ApplicationInsightsMetricForm(TaskForm):
    _model = ApplicationInsightsMetricTask
    metric = SelectField('Select metric')
    aggregation = SelectField("Select aggregation",
                              choices=[('avg', 'Average'), ('sum', 'Sum'), ('min', 'Min'), ('max', 'Max'),
                                       ('count', 'Count')])
    timespan = StringField('Timespan')
    nickname = StringField('Nickname')

    def __init__(self, *args, **kwargs):
        super(ApplicationInsightsMetricForm, self).__init__(*args, **kwargs)
        self.metric.choices = ApplicationInsightsMetricTask.choices()


class GitHubRepoStatusForm(TaskForm):
    _model = GitHubRepositoryStatusTask
    repo = StringField('Repository name')
    uses_webhook = BooleanField('Use WebHooks')


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


class GaugeForm(FlaskForm):
    nickname = StringField('Nickname')
    task_id = SelectField('Measured Task', coerce=int)
    min_val = IntegerField('Minimum value')
    max_val = IntegerField('Maximum value')

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_id.choices = [(t.id, t.name) for t in user.tasks]


class DevOpsTaskForm(FlaskForm):
    """
    Form for configuring DevOps build and release tasks for a given DevOps account.
    The form has 2 exposed fields, builds and releases. Each is a list of the inner forms,
     ReleaseFields and BuildFields. A factory method allows building a form from data.
     As a FlaskForm, this form will pre-populate itself based on request form data, if available.
    """

    class ReleaseFields(FlaskForm):
        class Meta(FlaskForm.Meta):
            csrf = False

        project = HiddenField()
        pipeline = HiddenField()
        environment = HiddenField()
        environment_id = HiddenField()
        definition_id = HiddenField()
        monitored = BooleanField()
        uses_webhook = BooleanField()

    class BuildFields(FlaskForm):
        class Meta(FlaskForm.Meta):
            csrf = False

        definition_id = HiddenField()
        project = HiddenField()
        pipeline = HiddenField()
        monitored = BooleanField()

    builds = FieldList(FormField(BuildFields))
    releases = FieldList(FormField(ReleaseFields))

    @classmethod
    def build(cls, all_tasks: Iterable, current_build_tasks: Iterable, current_release_tasks: Iterable):
        """
        Factory method for building a populated form.
        :param all_tasks: A consolidated list of all tasks
        :param current_build_tasks: A collection of currently monitored build tasks
        :param current_release_tasks: A collection of currently monitored release tasks
        :return: A DevOpsTaskForm populated with the input data
        """
        release_data = []
        build_data = []
        for task in all_tasks:
            if task.type == 'release':
                release_data.append({
                    'project': task.project,
                    'pipeline': task.name,
                    'environment': task.environment,
                    'environment_id': task.environment_id,
                    'definition_id': task.definition_id,
                    'monitored': task in current_release_tasks,
                    'uses_webhook': task.uses_webhook
                })
            if task.type == 'build':
                build_data.append({
                    'project': task.project,
                    'definition_id': task.definition_id,
                    'pipeline': task.name,
                    'monitored': task in current_build_tasks
                })

        form_data = {
            'builds': build_data,
            'releases': release_data
        }

        return DevOpsTaskForm(data=form_data)