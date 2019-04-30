import pytest
from cryptography.fernet import Fernet
from faker import Faker

from config import Config
import ambrose
from ambrose import db
from ambrose.models import TextMessage
from ambrose.services import DevOpsAccountService, ApplicationInsightsAccountService, UserService


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = Fernet.generate_key()


@pytest.fixture(scope='module')
def app():
    app = ambrose.build_app(TestConfig)
    with app.app_context():
        ambrose.db.create_all()
        yield app


@pytest.fixture(scope='module')
def client(app):
    return app.test_client()


@pytest.fixture(scope='session')
def password(faker):
    return faker.password()

@pytest.fixture(scope='module')
def user(app, faker, password):
    user = UserService.create_user(faker.email(), password)

    yield user

    ambrose.db.session.delete(user)
    ambrose.db.session.commit()


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
    account = DevOpsAccountService(None, cipher).new_account(
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
def appinsights_account(user, faker, cipher):
    account = ApplicationInsightsAccountService(None, cipher).new_account(
        user,
        faker.sha1(),
        faker.sha1(),
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
