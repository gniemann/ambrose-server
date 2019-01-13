import pytest

from config import Config
import devops_monitor
from devops_monitor.models import Task, User, Status
from devops_monitor.api import *


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    WTF_CSRF_ENABLED = False


@pytest.fixture(scope='module')
def client():
    app = devops_monitor.build_app(TestConfig)
    client = app.test_client()

    with app.app_context():
        yield client


@pytest.fixture(scope='module')
def session(client):
    devops_monitor.db.create_all()
    return devops_monitor.db.session


@pytest.fixture(scope='module')
def failed(session):
    failed_status = Status(value='failed')
    session.add(failed_status)
    return failed_status


@pytest.fixture(scope='module')
def succeeded(session):
    succeeded_status = Status(value='succeeded')
    session.add(succeeded_status)
    return succeeded_status


@pytest.fixture(scope='module')
def devops_service():
    class MockDevops:
        def get_release_summary(self, *args, **kwargs):
            return {
                'Dev': {
                    'name': 'Dev',
                    'status': 'succeeded',
                    'current': 'Release-2',
                },
                'Prod': {
                    'name': 'Prod',
                    'status': 'failed',
                    'current': 'Release-1'
                }
            }

    return MockDevops()

@pytest.fixture(scope='module')
def user(session):
    testUser = User(organization='ExampleOrg')
    devTask = Task(name='Dev', definitionId=1, project='MyProj', sort_order=0, type='release')
    prodTask = Task(name='Prod', definitionId=1, project='MyProj', sort_order=1, type='release')
    for obj in [testUser, devTask, prodTask]:
        session.add(obj)
    testUser.tasks.extend([devTask, prodTask])
    session.commit()

    return testUser

def test_task(failed, succeeded):
    task = Task()
    task.status = failed
    task.status = succeeded

    assert task.status == succeeded.value
    assert task.prev_status == failed.value


def test_user(session):
    user = User()
    task1 = Task(name='Task1', sort_order=2)
    task2 = Task(name='Task2', sort_order=1)
    session.add(task1)
    session.add(task2)
    user.tasks.append(task1)
    user.tasks.append(task2)
    session.add(user)
    session.commit()

    assert user.tasks == [task2, task1]


def test_build_release_statuses(user, devops_service):
    releases = build_release_statuses(user, devops_service)

    expected = [
        {
            'name': 'Dev',
            'current': 'Release-2',
            'status': 'succeeded'
        },
        {
            'name': 'Prod',
            'current': 'Release-1',
            'status': 'failed'
        }
    ]

    assert releases == expected