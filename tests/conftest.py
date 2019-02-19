import pytest
from cryptography.fernet import Fernet
from faker import Faker

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
        devops_monitor.db.create_all()
        yield app


@pytest.fixture(scope='module')
def client(app):
    return app.test_client()


@pytest.fixture(scope='module')
def user(app):
    user = devops_monitor.models.User(username='test@test.com')
    devops_monitor.db.session.add(user)
    devops_monitor.db.session.commit()

    yield user

    devops_monitor.db.session.delete(user)


@pytest.fixture(scope='session')
def faker():
    return Faker()