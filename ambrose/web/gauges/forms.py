from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField


class GaugeForm(FlaskForm):
    nickname = StringField('Nickname')
    task_id = SelectField('Measured Task', coerce=int)
    min_val = IntegerField('Minimum value')
    max_val = IntegerField('Maximum value')

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_id.choices = [(t.id, t.name) for t in user.tasks]
