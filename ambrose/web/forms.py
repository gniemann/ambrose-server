from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField
from wtforms.validators import InputRequired, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Username', [InputRequired()], render_kw={'required': True})
    password = PasswordField('Password', [InputRequired()], render_kw={'required': True})


class RegisterForm(FlaskForm):
    username = StringField('Username', [InputRequired()], render_kw={'required': True})
    password = PasswordField('Password',
                             [InputRequired(), EqualTo('confirm_password', message='Passwords did not match')],
                             render_kw={'required': True})
    confirm_password = PasswordField('Confirm Password', render_kw={'required': True})


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
