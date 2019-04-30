import functools
import inspect
from typing import Callable, Optional, Union

import flask_bcrypt as bcrypt
import flask_login
from flask_jwt_extended import get_jwt_identity, create_access_token, JWTManager

from ambrose.models import User, Device
from ambrose.services import UserService

jwt = JWTManager()


@jwt.user_identity_loader
def id_for_jwt(identity: Union[User, Device]):
    if isinstance(identity, User):
        return identity.username
    if isinstance(identity, Device):
        return identity.device_uuid


@jwt.user_loader_callback_loader
def user_from_jwt(identity):
    # the token is for either a device UUID or a username
    # try the device first, if its not a device, try the username next
    device = Device.by_uuid(identity)
    if device:
        return device.user

    return User.by_username(identity)


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
        return get_jwt_identity()

    @classmethod
    def jwt(cls, entity: Union[User, Device]):
        return create_access_token(identity=entity)
