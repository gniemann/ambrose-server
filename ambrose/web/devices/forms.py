from typing import List

from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectField, FieldList, FormField

from ambrose.models import StatusLight, Task


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