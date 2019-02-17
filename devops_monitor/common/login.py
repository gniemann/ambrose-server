import flask_login

from devops_monitor.models import User

login_manager = flask_login.LoginManager()
login_manager.login_view = 'web.login'


@login_manager.user_loader
def load_user(user_id):
    return User.by_id(user_id)



