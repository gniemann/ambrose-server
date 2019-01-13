

from . import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    organization = db.Column(db.String)

    tasks = db.relationship('Task', back_populates='user')