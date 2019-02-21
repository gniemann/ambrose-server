import functools
import inspect

import flask_bcrypt as bcrypt
import flask_login

from devops_monitor.models import User
from devops_monitor.services import UserService


class UserCredentialMismatchException(Exception):
    pass


class AuthService:
    @classmethod
    def login(cls, username, password):
        user = User.by_username(username)
        if not user or not bcrypt.check_password_hash(user.password, password):
            raise UserCredentialMismatchException()

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

    @classmethod
    def login_user(cls, user):
        flask_login.login_user(user)