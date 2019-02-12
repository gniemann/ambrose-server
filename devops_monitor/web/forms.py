from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, FormField, FieldList, HiddenField


class LoginForm(FlaskForm):
    username = StringField('Username', render_kw={'required': True})
    password = PasswordField('Password', render_kw={'required': True})


class RegisterForm(FlaskForm):
    username = StringField('Username', render_kw={'required': True})
    password = PasswordField('Password', render_kw={'required': True})
    confirm_password = PasswordField('Confirm Password', render_kw={'required': True})
    organization = StringField('Organization', render_kw={'required': True})
    token = StringField('DevOps Personal Access Token', render_kw={'required': True})


class SettingsForm(FlaskForm):
    username = StringField('Username', render_kw={'required': True})
    token = StringField('New DevOps Personal Access Token')


class SetupForm(FlaskForm):
    project = StringField('Project', render_kw={'required': True})

