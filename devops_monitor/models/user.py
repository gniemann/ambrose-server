import flask_login
from sqlalchemy.ext.associationproxy import association_proxy

from devops_monitor.models.light import StatusLight
from . import db, DevOpsAccount, Message


class User(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)

    accounts = db.relationship('Account', back_populates='user')

    tasks = db.relationship('Task', back_populates='user', cascade='all, delete, delete-orphan')
    _messages = db.relationship('Message', cascade='all, delete, delete-orphan')

    messages = association_proxy('_messages', 'text', creator=lambda text: Message(text=text))
    lights = db.relationship('StatusLight', cascade='all, delete, delete-orphan')

    @classmethod
    def by_username(cls, username):
        return cls.query.filter_by(username=username).one_or_none()

    @classmethod
    def by_id(cls, user_id):
        return cls.query.get(user_id)

    @property
    def devops_account(self):
        for account in self.accounts:
            if isinstance(account, DevOpsAccount):
                return account
        return None

    def light_for_slot(self, index):
        return StatusLight.by_id(self.id, index)

    def set_task_for_light(self, task, index):
        light = self.light_for_slot(index)
        if light:
            light.task = task
        else:
            light = StatusLight(slot=index, user_id=self.id)
            light.task = task
            self.lights.append(light)

    def resize_lights(self, count):
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


    def add_message(self, text):
        self.messages.append(text)

    def clear_messages(self):
        self.messages.clear()

    def add_account(self, account):
        self.accounts.append(account)

    def add_task(self, task):
        self.tasks.append(task)