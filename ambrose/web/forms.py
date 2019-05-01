from __future__ import annotations

from typing import List

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FormField, FieldList, HiddenField, SelectField, IntegerField
from wtforms.validators import InputRequired, EqualTo

from ambrose.models import StatusLight, Task


class LoginForm(FlaskForm):
    username = StringField('Username', [InputRequired()], render_kw={'required': True})
    password = PasswordField('Password', [InputRequired()], render_kw={'required': True})


class RegisterForm(FlaskForm):
    username = StringField('Username', [InputRequired()], render_kw={'required': True})
    password = PasswordField('Password',
                             [InputRequired(), EqualTo('confirm_password', message='Passwords did not match')],
                             render_kw={'required': True})
    confirm_password = PasswordField('Confirm Password', render_kw={'required': True})


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
