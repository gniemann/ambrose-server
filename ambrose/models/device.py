from __future__ import annotations

import uuid
from typing import Optional

from . import db, StatusLight, Task


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_uuid = db.Column(db.String, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String)
    supports_messages = db.Column(db.Boolean)
    last_contact = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', uselist=False, back_populates='devices')
    lights = db.relationship('StatusLight', cascade='all, delete, delete-orphan')

    @classmethod
    def by_id(cls, device_id):
        return cls.query.get(device_id)

    @classmethod
    def by_uuid(cls, device_uuid: str) -> Optional[Device]:
        return cls.query.filter_by(device_uuid=device_uuid).one_or_none()

    def __init__(self, name: str, num_lights: int, num_gauges: int, supports_messages: bool):
        self.name = name
        self.supports_messages = supports_messages

        for slot in range(1, num_lights + 1):
            self.set_task_for_light(None, slot)

    def light_for_slot(self, index: int) -> Optional[StatusLight]:
        return StatusLight.by_id(self.id, index)

    def set_task_for_light(self, task: Optional[Task], index: int):
        light = self.light_for_slot(index)
        if light:
            light.task = task
        else:
            light = StatusLight(slot=index, device_id=self.id)
            light.task = task
            self.lights.append(light)