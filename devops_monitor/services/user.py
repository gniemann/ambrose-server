from typing import Any, Mapping

import flask_bcrypt as bcrypt

from devops_monitor.common import db_transaction
from devops_monitor.models import User, Task, DateTimeMessage, TextMessage, TaskMessage, Message
from devops_monitor.services import UnauthorizedAccessException


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

    def update_lights(self, data: Mapping[str, Any]):
        with db_transaction():
            if data['num_lights'] != len(self.user.lights):
                self.user.resize_lights(data['num_lights'])
                return

            for light_data in data['lights']:
                task_id = light_data['task']
                task = Task.by_id(task_id) if task_id >= 0 else None
                self.user.set_task_for_light(task, light_data['slot'])

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