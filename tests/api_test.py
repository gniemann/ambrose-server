import pytest

from devops_monitor.api import AccessTokenSchema
from devops_monitor.models import Message, TextMessage, ApplicationInsightsMetricTask, db, Task
from devops_monitor.services import UserService, AuthService


@pytest.fixture(scope='module')
def access_token(client, user):
    return AuthService.jwt(user)


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

    resp = client.delete('/api/messages/{}'.format(message_id), headers={'Authorization': 'Bearer {}'.format(access_token)})

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