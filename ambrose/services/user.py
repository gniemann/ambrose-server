import datetime
from typing import Any, Mapping, List

import flask_bcrypt as bcrypt

from ambrose.common import db_transaction
from ambrose.models import User, DateTimeMessage, TextMessage, TaskMessage, Message, Device, Task, Gauge, LightSettings
from ambrose.services import UnauthorizedAccessException


class UserService:
    def __init__(self, user):
        self.user = user

    @classmethod
    def create_user(cls, username: str, password: str) -> User:
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username.lower(), password=pw_hash)

        with db_transaction() as session:
            session.add(user)

        return user

    def _add_message(self, message: Message) -> Message:
        with db_transaction():
            self.user.add_message(message)
        return message

    def _delete(self, obj):
        with db_transaction() as session:
            session.delete(obj)

    def add_message(self, text: str):
        return self._add_message(TextMessage(text=text))

    def update_lights(self, device_id: int, data: Mapping[str, Any]):
        device = self.get_device(device_id)
        with db_transaction():
            for light_data in data['lights']:
                task_id = light_data['task']
                task = Task.by_id(task_id) if task_id >= 0 else None
                device.set_task_for_light(task, light_data['slot'])

    def add_datetime_message(self, format_string: str, date_format: str, timezone: str) -> Message:
        return self._add_message(DateTimeMessage(
            text=format_string,
            dateformat=date_format,
            timezone=timezone
        ))

    def add_task_message(self, task_id: int, format_string: str) -> Message:
        task = Task.by_id(task_id)
        return self._add_message(TaskMessage(text=format_string, task=task))

    def get_message(self, message_id: int) -> Message:
        message = Message.by_id(message_id)
        if message not in self.user.messages:
            raise UnauthorizedAccessException()

        return message

    def update_message(self, message: Message, data: Mapping[str, Any]):
        if message not in self.user.messages:
            raise UnauthorizedAccessException

        with db_transaction():
            message.update(data)

    def create_message(self, message_type: str, data: Mapping[str, Any]):
        return self._add_message(Message.new_message(message_type, data))

    def delete_message(self, message_id: int):
        self._delete(self.get_message(message_id))

    def get_task(self, task_id) -> Task:
        task = Task.by_id(task_id)
        if task not in self.user.tasks:
            raise UnauthorizedAccessException()

        return task

    def delete_task(self, task_id: int):
        self._delete(self.get_task(task_id))

    def update_task(self, task: Task, data: Mapping[str, Any]):
        if task not in self.user.tasks:
            raise UnauthorizedAccessException

        with db_transaction():
            task.update(data)

    def add_gauge(self, task_id: int, min_val: int, max_val: int, nickname: str):
        with db_transaction():
            self.user.add_gauge(Gauge(min_val=min_val, max_val=max_val, task_id=task_id, nickname=nickname))

    def add_device(self, name: str, lights: int, gagues: int, supports_messages: bool) -> Device:
        with db_transaction():
            device = Device(name, lights, gagues, supports_messages)
            self.user.add_device(device)
            return device

    def get_device(self, device_id):
        device = Device.by_id(device_id)
        if device not in self.user.devices:
            raise UnauthorizedAccessException

        return device

    def delete_device(self, device_id):
        self._delete(self.get_device(device_id))

    def mark_tasks_viewed(self):
        with db_transaction():
            for task in self.user.tasks:
                task.has_changed = False

    def mark_device_visit(self, device: Device):
        with db_transaction():
            device.last_contact = datetime.datetime.now()
            for light in device.lights:
                if light:
                    light.task.has_changed = False

    def add_setting(self, status: str, red: int, green: int, blue: int):
        with db_transaction():
            self.user.add_setting(LightSettings(status=status, color_red=red, color_blue=blue, color_green=green))

    def edit_settings(self, settings: List[Mapping[str, Any]]):
        with db_transaction():
            for setting in settings:
                record = LightSettings.by_id(setting['setting_id'])
                if not record:
                    continue
                record.status = setting['status']
                record.color_red = setting['red']
                record.color_green = setting['green']
                record.color_blue = setting['blue']
