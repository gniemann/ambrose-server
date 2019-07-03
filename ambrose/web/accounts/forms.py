from __future__ import annotations

from typing import Iterable

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, HiddenField, BooleanField, FieldList, FormField
from wtforms.validators import InputRequired

from ambrose.models import Account, GitHubRepositoryStatusTask, ApplicationInsightsMetricTask, HealthcheckTask
from ambrose.web.forms import TaskForm


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ApplicationInsightsAccountForm(AccountForm):
    application_id = StringField('Application ID', [InputRequired()], render_kw={'required': True})
    api_key = StringField('API Key', [InputRequired()], render_kw={'required': True})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class GitHubAccountForm(AccountForm):
    token = StringField('Personal Access Token', [InputRequired()], render_kw={'required': True})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class WebAccountForm(AccountForm):
    base_url = StringField('Base URL', [InputRequired()], render_kw={'required': True})


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
        current = BooleanField()
        uses_webhook = BooleanField()

    class BuildFields(FlaskForm):
        class Meta(FlaskForm.Meta):
            csrf = False

        definition_id = HiddenField()
        project = HiddenField()
        pipeline = HiddenField()
        current = BooleanField()

    builds = FieldList(FormField(BuildFields))
    releases = FieldList(FormField(ReleaseFields))

    @classmethod
    def build(cls, build_tasks: Iterable, release_tasks: Iterable) -> DevOpsTaskForm:
        """
        Factory method for building a populated form.
        :param build_tasks: The build tasks
        :param release_tasks: The release tasks
        :return: A DevOpsTaskForm
        """

        form_data = {
            'builds': build_tasks,
            'releases': release_tasks
        }

        return DevOpsTaskForm(data=form_data)


class GitHubRepoStatusForm(TaskForm):
    _model = GitHubRepositoryStatusTask
    repo = StringField('Repository name')
    uses_webhook = BooleanField('Use WebHooks')


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


class HealthcheckTaskForm(TaskForm):
    _model = HealthcheckTask
    path = StringField('Healthcheck Path')
