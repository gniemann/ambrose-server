from __future__ import annotations

from typing import Optional

import flask_login

from ambrose.models.device import Device
from . import db, StatusLight, Task, Message, Account, DevOpsAccount, Gauge


class User(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)

    accounts = db.relationship('Account', back_populates='user')

    tasks = db.relationship('Task', back_populates='user', cascade='all, delete, delete-orphan')
    messages = db.relationship('Message', cascade='all, delete, delete-orphan')

    lights = db.relationship('StatusLight', cascade='all, delete, delete-orphan')
    gauges = db.relationship('Gauge', cascade='all, delete, delete-orphan')
    devices = db.relationship('Device', cascade='all, delete, delete-orphan', back_populates='user')

    @classmethod
    def by_username(cls, username: str) -> Optional[User]:
        return cls.query.filter_by(username=username).one_or_none()

    @classmethod
    def by_id(cls, user_id: int) -> Optional[User]:
        return cls.query.get(user_id)

    @property
    def devops_account(self) -> Optional[DevOpsAccount]:
        for account in self.accounts:
            if isinstance(account, DevOpsAccount):
                return account
        return None

    def light_for_slot(self, index: int) -> Optional[StatusLight]:
        return StatusLight.by_id(self.id, index)

    def set_task_for_light(self, task: Optional[Task], index: int):
        light = self.light_for_slot(index)
        if light:
            light.task = task
        else:
            light = StatusLight(slot=index, user_id=self.id)
            light.task = task
            self.lights.append(light)

    def resize_lights(self, count: int):
        lights = self.lights
        current_count = len(lights)
        if count == current_count:
            return
        if count > current_count:
            last_slot = lights[-1].slot if current_count > 0 else 0
            diff = count - current_count
            for slot in range(last_slot + 1, last_slot + diff + 1):
                self.set_task_for_light(None, slot)
        else:
            for light in lights[count:]:
                self.lights.remove(light)

    def add_message(self, message: Message):
        self.messages.append(message)

    def add_account(self, account: Account):
        self.accounts.append(account)

    def add_task(self, task: Task):
        self.tasks.append(task)

    def remove_message(self, message: Message):
        self.messages.remove(message)

    def add_gauge(self, gauge: Gauge):
        self.gauges.append(gauge)

    def add_device(self, device: Device):
        self.devices.append(device)