import functools
import inspect
from typing import Callable, Optional

import flask_bcrypt as bcrypt
import flask_login
from flask_jwt_extended import get_jwt_identity, create_access_token

from ambrose.models import User
from ambrose.services import UserService


class UserCredentialMismatchException(Exception):
    pass


class AuthService:
    @classmethod
    def login(cls, username: str, password: str) -> User:
        user = User.by_username(username.lower())
        if not user or not bcrypt.check_password_hash(user.password, password):
            raise UserCredentialMismatchException()

        flask_login.login_user(user)
        return user

    @classmethod
    def logout(cls):
        flask_login.logout_user()

    @staticmethod
    def auth_required(func: Callable) -> Callable:
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
    def login_user(cls, user: User):
        flask_login.login_user(user)

    @classmethod
    def current_user(cls):
        return flask_login.current_user

    @classmethod
    def current_api_user(cls) -> Optional[User]:
        username = get_jwt_identity()
        return User.by_username(username)

    @classmethod
    def jwt(cls, user):
        return create_access_token(identity=user.username)