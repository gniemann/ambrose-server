import pytest
from cryptography.fernet import Fernet

from config import Config
import devops_monitor


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = Fernet.generate_key()

@pytest.fixture(scope='module')
def app():
    app = devops_monitor.build_app(TestConfig)
    with app.app_context():
        seed_database()

    return app

@pytest.fixture(scope='module')
def client(app):
    client = app.test_client()

    with app.app_context():
        yield client


def seed_database():
    devops_monitor.db.create_all()

    user = devops_monitor.models.User(
        username='test@test.com'
    )
    devops_monitor.db.session.add(user)
    devops_monitor.db.session.commit()


@pytest.fixture()
def authenticated_user(app):
    @devops_monitor.login_manager.request_loader
    def load_user_from_request(request):
        return devops_monitor.models.User.query.first()
        

@pytest.mark.parametrize('route', [
    '/web/',
    '/web/messages/',
    '/web/accounts/',
    '/web/edit'
])
def test_unauthenticated(client, route):
    resp = client.get(route)

    assert resp.status_code == 302
    assert '/web/login' in resp.headers['Location']

@pytest.mark.parametrize('route', [
    '/web/',
    '/web/messages/',
    '/web/edit',
    '/web/accounts/',
    '/web/accounts/devops',
    '/web/accounts/application_insights',
    '/web/tasks/'
])
def test_index_authenticated(client, route, authenticated_user):
    resp = client.get(route)

    assert resp.status_code == 200