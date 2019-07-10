from __future__ import annotations

from typing import Optional

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

    @classmethod
    def by_id(cls, setting_is: int) -> Optional[LightSettings]:
        return cls.query.get(setting_is)

    def __init__(self, status, color_red=0, color_green=0, color_blue=0):
        self.status = status
        self.color_red = color_red
        self.color_green = color_green
        self.color_blue = color_blue
