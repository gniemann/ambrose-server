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


class MessageForm(FlaskForm):
    message = StringField('Message', [InputRequired()], render_kw={'required': True})


class DevOpsAccountForm(FlaskForm):
    username = StringField('Username', [InputRequired()], render_kw={'required': True})
    organization = StringField('Organization', [InputRequired()], render_kw={'required': True})
    token = StringField('DevOps Personal Access Token', [InputRequired()], render_kw={'required': True})
    nickname = StringField('Nickname')


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
    type = SelectField('Select task type', choices=[(0, 'DateTime Message')], coerce=int)


class DateTimeMessageForm(FlaskForm):
    dateformat = StringField('Enter datetime format')
    message = StringField('Enter message', render_kw={'required': True})
