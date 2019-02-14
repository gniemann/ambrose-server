import flask_login

from devops_monitor.models import User

login_manager = flask_login.LoginManager()
login_manager.login_view = 'web.login'

class WebUser(flask_login.UserMixin):
    pass

@login_manager.user_loader
def load_user(username):
    user = User.by_username(username)

    if not user:
        return None

    web_user = WebUser()
    web_user.id = username
    return web_user
