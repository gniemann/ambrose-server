from __future__ import annotations

import uuid
from typing import Optional

from . import db


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_uuid = db.Column(db.String, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', uselist=False, back_populates='devices')

    @classmethod
    def by_uuid(cls, device_uuid: str) -> Optional[Device]:
        return cls.query.filter_by(device_uuid=device_uuid).one_or_none()