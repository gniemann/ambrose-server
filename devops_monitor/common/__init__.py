import contextlib
import functools

from cryptography.fernet import Fernet
from flask import current_app

from devops_monitor import db
from .login import login_manager


def cipher_required(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        cipher = Fernet(current_app.secret_key)
        return func(*args, cipher=cipher, **kwargs)

    return inner


@contextlib.contextmanager
def db_transaction():
    try:
        yield db.session
        db.session.commit()
    except:
        db.session.rollback()
        raise
