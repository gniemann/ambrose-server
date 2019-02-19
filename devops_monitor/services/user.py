import functools
import inspect

import flask_bcrypt as bcrypt
import flask_login

from devops_monitor.common import db_transaction
from devops_monitor.models import User, Task, DateTimeMessage, TextMessage, TaskMessage, Message
from devops_monitor.services import UnauthorizedAccessException


class UserCredentialMismatchException(Exception):
    pass


class UserService:
    def __init__(self, user):
        self.user = user

    @classmethod
    def login(cls, username, password):
        user = User.by_username(username)
        if not user or not bcrypt.check_password_hash(user.password, password):
            raise UserCredentialMismatchException()

        flask_login.login_user(user)
        return user

    @classmethod
    def create_user(cls, username, password):
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=pw_hash)

        with db_transaction() as session:
            session.add(user)

        flask_login.login_user(user)

        return user

    @classmethod
    def logout(cls):
        flask_login.logout_user()

    @staticmethod
    def auth_required(func):
        signature = inspect.signature(func)

        @functools.wraps(func)
        @flask_login.login_required
        def inner(*args, **kwargs):
            added_kwargs = {}

            if 'user' in signature.parameters:
                added_kwargs['user'] = flask_login.current_user
            if 'user_service' in signature.parameters:
                added_kwargs['user_service'] = UserService(flask_login.current_user)

            return func(*args, **added_kwargs, **kwargs)

        return inner

    def add_message(self, message):
        with db_transaction():
            self.user.add_message(TextMessage(text=message))

    def update_lights(self, data):
        with db_transaction():
            if data['num_lights'] != len(self.user.lights):
                self.user.resize_lights(data['num_lights'])
                return

            for light_data in data['lights']:
                task_id = light_data['task']
                task = Task.by_id(task_id) if task_id >= 0 else None
                self.user.set_task_for_light(task, light_data['slot'])

    def add_datetime_message(self, format_string, date_format, timezone):
        with db_transaction():
            self.user.add_message(DateTimeMessage(
                text=format_string,
                dateformat=date_format,
                timezone=timezone
            ))

    def add_task_message(self, task_id, format_string):
        task = Task.by_id(task_id)
        with db_transaction():
            self.user.add_message(TaskMessage(text=format_string, task=task))

    def get_message(self, message_id):
        message = Message.by_id(message_id)
        if message not in self.user.messages:
            raise UnauthorizedAccessException()

        return message
