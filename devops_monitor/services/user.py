import flask_bcrypt as bcrypt
import flask_login

from devops_monitor.common import db_transaction
from devops_monitor.models import User, Task, DateTimeMessage, TextMessage, TaskMessage, Message
from devops_monitor.services import UnauthorizedAccessException


class UserService:
    def __init__(self, user):
        self.user = user

    @classmethod
    def create_user(cls, username, password):
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=pw_hash)

        with db_transaction() as session:
            session.add(user)

        return user

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
