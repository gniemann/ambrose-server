import pytest
from cryptography.fernet import Fernet
from faker import Faker

from config import Config
import devops_monitor
from devops_monitor import db
from devops_monitor.models import TextMessage
from devops_monitor.services import DevOpsAccountService


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


@pytest.fixture(scope='module')
def token(faker):
    return faker.sha1()


@pytest.fixture(scope='module')
def cipher():
    return Fernet(Fernet.generate_key())


@pytest.fixture(scope='module')
def devops_account(user, faker, token, cipher):
    account = DevOpsAccountService(cipher).new_account(
        user,
        faker.email(),
        faker.word(),
        token,
        faker.word()
    )

    yield account

    db.session.delete(account)
    db.session.commit()


@pytest.fixture(scope='module')
def text_message(user, faker):
    msg = TextMessage(text=faker.sentence())
    user.add_message(msg)
    db.session.commit()

    yield msg

    db.session.delete(msg)
    db.session.commit()
