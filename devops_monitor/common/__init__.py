import functools

from cryptography.fernet import Fernet
from flask import current_app

from devops_monitor import db
from .login import login_manager, WebUser

def cipher_required(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        cipher = Fernet(current_app.secret_key)
        return func(*args, cipher=cipher, **kwargs)

    return inner


def db_required(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            resp = func(*args, session=db.session, **kwargs)
            db.session.commit()
            return resp
        except:
            db.session.rollback()
            raise

    return inner