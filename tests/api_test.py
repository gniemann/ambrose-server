import pytest

import ambrose
from ambrose.models import Message, TextMessage, db, Device, Task, ApplicationInsightsMetricTask
from ambrose.services import AuthService, UserService


@pytest.fixture(scope='function')
def access_token(client, user):
    return AuthService.jwt(user)


@pytest.fixture(scope='function')
def user(app, faker, password):
    user = UserService.create_user(faker.email(), password)

    yield user

    ambrose.db.session.delete(user)
    ambrose.db.session.commit()


def test_login(client, user, password):
    data = {
        'username': user.username,
        'password': password
    }

    resp = client.post('/api/login', json=data)

    assert resp.status_code == 200
    assert resp.json is not None
    assert resp.json.get('access_token') is not None


def test_delete_message(client, user, access_token):
    message = TextMessage(text='Hello', user_id=user.id)
    db.session.add(message)
    db.session.commit()
    message_id = message.id

    resp = client.delete('/api/messages/{}'.format(message_id),
                         headers={'Authorization': 'Bearer {}'.format(access_token)})

    assert resp.status_code == 204
    assert Message.by_id(message_id) is None


def test_delete_task(client, user, access_token):
    task = ApplicationInsightsMetricTask(metric='requests/count', user=user)
    db.session.add(task)
    db.session.commit()
    task_id = task.id

    resp = client.delete('/api/tasks/{}'.format(task_id), headers={'Authorization': 'Bearer {}'.format(access_token)})
    assert resp.status_code == 204
    assert Task.by_id(task_id) is None


def test_delete_device(client, user, access_token):
    device = Device('my device', 3, 0, True)
    user.add_device(device)

    db.session.add(device)
    db.session.add(user)
    db.session.commit()
    device_id = device.id

    resp = client.delete('/api/devices/{}'.format(device_id), headers={'Authorization': 'Bearer {}'.format(access_token)})
    assert resp.status_code == 204
    assert Device.by_id(device_id) is None

def test_register_device(client, user , password):
    data = {
        'name': 'My Device',
        'lights': 3,
        'messages': True,
        'gauges': 0,
    }

    resp = client.post('/api/devices/register', json=data)

    assert resp.status_code == 200
    assert resp.json is not None
    assert resp.json.get('access_token') is not None
