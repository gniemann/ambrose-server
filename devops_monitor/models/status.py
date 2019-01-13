

from . import db


class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String, unique=True)

    @classmethod
    def by_value(cls, value):
        return cls.query.filter_by(value=value).first()