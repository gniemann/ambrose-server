from flask import Blueprint, render_template, abort, redirect, url_for
import flask_login
import flask_bcrypt as bcrypt

from devops_monitor.models import User
from .forms import LoginForm

login_manager = flask_login.LoginManager()
login_manager.login_view = 'web.login'

web_bp = Blueprint('web', __name__, template_folder='templates')

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


@web_bp.route('/')
@flask_login.login_required
def index():
    user = User.by_username(flask_login.current_user.id)

    return render_template('index.html', tasks=user.tasks)


@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.by_username(form.username.data)
        if not user or not bcrypt.check_password_hash(user.password, form.password.data):
            abort(401)

        web_user = WebUser()
        web_user.id = user.username
        flask_login.login_user(web_user)

        return redirect(url_for('.index'))

    return render_template('login.html', form=form)


@web_bp.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for('.login'))
