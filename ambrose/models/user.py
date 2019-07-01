from __future__ import annotations

from typing import Optional

import flask_login

from .device import Device
from . import db, StatusLight, Message, Account, Gauge
from .task import Task


class User(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)

    accounts = db.relationship('Account', back_populates='user')

    tasks = db.relationship('Task', back_populates='user', cascade='all, delete, delete-orphan')
    messages = db.relationship('Message', cascade='all, delete, delete-orphan')

    gauges = db.relationship('Gauge', cascade='all, delete, delete-orphan')
    devices = db.relationship('Device', cascade='all, delete, delete-orphan', back_populates='user')

    @classmethod
    def by_username(cls, username: str) -> Optional[User]:
        return cls.query.filter_by(username=username).one_or_none()

    @classmethod
    def by_id(cls, user_id: int) -> Optional[User]:
        return cls.query.get(user_id)

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