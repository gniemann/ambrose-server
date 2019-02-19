import flask_login
import flask_bcrypt as bcrypt
from flask import abort

from devops_monitor.models import User

login_manager = flask_login.LoginManager()
login_manager.login_view = 'web.login'


@login_manager.user_loader
def load_user(user_id):
    return User.by_id(user_id)


@login_manager.request_loader
def request_loader(request):
    if not request.authorization:
        return None

    user = User.by_username(request.authorization.username)
    if user and bcrypt.check_password_hash(user.password, request.authorization.password):
        return user

    abort(401)
