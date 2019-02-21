import flask_login
import pytest

from devops_monitor.models import User, db
from devops_monitor.services import UserService, AuthService


@pytest.fixture(scope='module')
def username(faker):
    return faker.email()

@pytest.fixture(scope='module')
def password(faker):
    return faker.password()

@pytest.fixture(scope='function')
def known_user(app, username, password):
    with app.test_request_context('/'):
        u = UserService.create_user(username, password)

    yield u

    db.session.delete(u)
    db.session.commit()

def test_create_user(app, username, password):
    with app.test_request_context('/'):
        new_user = UserService.create_user(username, password)
        AuthService.login_user(new_user)
        assert flask_login.current_user == new_user

    user = User.by_username(username)
    assert user is not None

    # ensure that the password is hashed
    assert user.password != password

    db.session.delete(user)


def test_login(app, known_user, username, password):
    with app.test_request_context('/'):
        assert flask_login.current_user != known_user

        user = AuthService.login(username, password)

        assert user == known_user
        assert flask_login.current_user == known_user




