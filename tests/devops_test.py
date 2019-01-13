import pytest

from config import Config
import devops_monitor
from devops_monitor.models import Task, User, Status

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    WTF_CSRF_ENABLED = False

@pytest.fixture(scope='module')
def client():
    app = devops_monitor.build_app(TestConfig)
    client = app.test_client()

    with app.app_context():
        seed_database()
        yield client

def seed_database():
    devops_monitor.db.create_all()

    succeeded = Status(value='succeeded')
    failed = Status(value='failed')

    devops_monitor.db.session.add(succeeded)
    devops_monitor.db.session.add(failed)

    devops_monitor.db.session.commit()


def test_task(client):
    task = Task()
    task.status = Status.by_value('failed')
    task.status = Status.by_value('succeeded')

    assert task.status == 'succeeded'
    assert task.prev_status == 'failed'
