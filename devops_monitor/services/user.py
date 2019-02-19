import functools

import flask_bcrypt as bcrypt
import flask_login

from devops_monitor.common import db_transaction
from devops_monitor.models import User, Task, DateTimeMessage, TextMessage, TaskMessage


class UserCredentialMismatchException(Exception):
    pass

class UserService:
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
        @functools.wraps(func)
        @flask_login.login_required
        def inner(*args, **kwargs):
            return func(*args, user=flask_login.current_user, **kwargs)

        return inner

    @classmethod
    def add_message(cls, user, message):
        with db_transaction():
            user.add_message(TextMessage(text=message))

    @classmethod
    def clear_messages(cls, user):
        with db_transaction():
            user.clear_messages()

    @classmethod
    def update_lights(cls, user, data):
        with db_transaction():
            if data['num_lights'] != len(user.lights):
                user.resize_lights(data['num_lights'])
                return

            for light_data in data['lights']:
                task_id = light_data['task']
                task = Task.by_id(task_id) if task_id >= 0 else None
                user.set_task_for_light(task, light_data['slot'])

    @classmethod
    def add_datetime_message(cls, user, format_string, date_format):
        with db_transaction():
            user.add_message(DateTimeMessage(text=format_string, dateformat=date_format))


    @classmethod
    def add_task_message(cls, user, task_id, format_string):
        task = Task.by_id(task_id)
        with db_transaction():
            user.add_message(TaskMessage(text=format_string, task=task))