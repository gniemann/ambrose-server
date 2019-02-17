import flask_login
from sqlalchemy.ext.associationproxy import association_proxy

from . import db, DevOpsAccount, Message


class User(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)

    accounts = db.relationship('Account', back_populates='user')

    tasks = db.relationship('Task', back_populates='user', order_by='Task.sort_order', cascade='all, delete, delete-orphan')
    _messages = db.relationship('Message', cascade='all, delete, delete-orphan')

    messages = association_proxy('_messages', 'text')

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

    def add_message(self, text):
        self.messages.append(text)

    def clear_messages(self):
        self.messages.clear()

    def add_account(self, account):
        self.accounts.append(account)