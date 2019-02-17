from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, FormField, FieldList, HiddenField
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
