import functools

import flask_bcrypt as bcrypt
import flask_login

from devops_monitor.common import db_transaction
from devops_monitor.models import User

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
        pw_hash = bcrypt.generate_password_hash(password)
        user = User(username=username, password=pw_hash)

        with db_transaction() as session:
            session.add(user)

        flask_login.logout_user(user)

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
            user.add_message(message)

    @classmethod
    def clear_messages(cls, user):
        with db_transaction():
            user.clear_messages()