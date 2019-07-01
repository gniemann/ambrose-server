from . import db


class LightSettings(db.Model):
    __tablename__ = 'light_settings'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String)
    color_red = db.Column(db.Integer, default=0)
    color_green = db.Column(db.Integer, default=0)
    color_blue = db.Column(db.Integer, default=0)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', uselist=False, back_populates='light_settings')

