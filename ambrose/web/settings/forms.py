from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import InputRequired


class LightSettingsForm(FlaskForm):
    status = StringField('Status', [InputRequired()], render_kw={'required': True})
    red = IntegerField('Red Value', default=0)
    green = IntegerField('Green Value', default=0)
    blue = IntegerField('Blue Value', default=0)