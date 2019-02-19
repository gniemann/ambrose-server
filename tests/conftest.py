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
        devops_monitor.db.create_all()

    return app

@pytest.fixture(scope='module')
def client(app):
    client = app.test_client()

    with app.app_context():
        yield client