import pytz
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, FormField, FieldList, HiddenField, SelectField, IntegerField
from wtforms.validators import InputRequired, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Username', [InputRequired()], render_kw={'required': True})
    password = PasswordField('Password', [InputRequired()], render_kw={'required': True})


class RegisterForm(FlaskForm):
    username = StringField('Username', [InputRequired()], render_kw={'required': True})
    password = PasswordField('Password', [InputRequired(), EqualTo('confirm_password', message='Passwords did not match')], render_kw={'required': True})
    confirm_password = PasswordField('Confirm Password', render_kw={'required': True})


class NewAccountForm(FlaskForm):
    type = SelectField('Select new account type')


class DevOpsAccountForm(FlaskForm):
    username = StringField('Username', [InputRequired()], render_kw={'required': True})
    organization = StringField('Organization', [InputRequired()], render_kw={'required': True})
    token = StringField('DevOps Personal Access Token', [InputRequired()], render_kw={'required': True})
    nickname = StringField('Nickname')


class ApplicationInsightsAccountForm(FlaskForm):
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
    type = SelectField('Select task type')


class ApplicationInsightsMetricForm(FlaskForm):
    metric = SelectField('Select metric')
    nickname = StringField('Nickname')


class NewMessageForm(FlaskForm):
    type = SelectField('Select task type')


class MessageForm(FlaskForm):
    message = StringField('Enter message', render_kw={'required': True})


class DateTimeMessageForm(MessageForm):
    dateformat = StringField('Enter datetime format')
    message = StringField('Enter message', render_kw={'required': True})
    timezone = SelectField('Select display timezone', choices=[(tz, tz) for tz in pytz.all_timezones if tz.startswith('US')])


class TaskMessageForm(MessageForm):
    task = SelectField('Select task', coerce=int)