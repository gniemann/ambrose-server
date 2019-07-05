import pytest

import ambrose
from ambrose.models import ApplicationInsightsMetricTask
from ambrose.models.account import ApplicationInsightsAccount, DevOpsAccount


@pytest.fixture()
def authenticated_user(user):
    @ambrose.login_manager.request_loader
    def load_user_from_request(request):
        return user
        

@pytest.mark.parametrize('route', [
    '/web/',
    '/web/messages/',
    '/web/accounts/',
    '/web/devices/',
    '/web/settings/',
    '/web/tasks/'
])
def test_unauthenticated(client, route):
    resp = client.get(route)

    assert resp.status_code == 302
    assert '/web/login' in resp.headers['Location']

@pytest.mark.usefixtures('authenticated_user')
@pytest.mark.parametrize('route', [
    '/web/',
    '/web/messages/',
    '/web/messages/new/text',
    '/web/messages/new/datetime',
    '/web/messages/new/task',
    '/web/accounts/',
    '/web/accounts/devops',
    '/web/accounts/applicationinsights',
    '/web/tasks/'
])
def test_index_authenticated(client, route):
    resp = client.get(route)

    assert resp.status_code == 200


@pytest.mark.usefixtures('authenticated_user')
def test_accounts(client, devops_account):
    resp = client.get('/web/accounts/')

    assert resp.status_code == 200
    assert devops_account.nickname in resp.data.decode('utf-8')


@pytest.mark.usefixtures('authenticated_user')
def test_tasks(client, devops_account):
    resp = client.get('/web/tasks/')

    assert resp.status_code == 200
    assert devops_account.nickname in resp.data.decode('utf-8')


@pytest.mark.usefixtures('authenticated_user')
def test_edit_message(client, text_message):
    resp = client.get('/web/messages/{}'.format(text_message.id))

    assert resp.status_code == 200
    assert text_message.text in resp.data.decode('utf-8')

@pytest.mark.usefixtures('authenticated_user')
def test_post_new_devops_account(client, user, faker):
    data = {
        'username': faker.email(),
        'organization': faker.word(),
        'token': faker.sha1(),
        'nickname': faker.word()
    }

    resp = client.post('/web/accounts/devops', data=data)

    assert resp.status_code == 302
    assert resp.headers['Location'].endswith('/web/accounts/')

    new_account = DevOpsAccount.query.filter_by(username=data['username']).one_or_none()
    assert new_account is not None
    assert new_account.token != data['token']
    assert new_account.organization == data['organization']
    assert new_account.nickname == data['nickname']
    assert new_account in user.accounts

@pytest.mark.usefixtures('authenticated_user')
def test_post_new_appinsights_account(client, user, faker):
    data = {
        'application_id': faker.sha1(),
        'api_key': faker.sha1()
    }

    resp = client.post('/web/accounts/applicationinsights', data=data)

    assert resp.status_code == 302
    assert resp.headers['Location'].endswith('/web/accounts/')

    new_account = ApplicationInsightsAccount.query.filter_by(application_id=data['application_id']).one_or_none()
    assert new_account is not None
    assert new_account.api_key != data['api_key']
    assert new_account in user.accounts

@pytest.mark.usefixtures('authenticated_user')
def test_get_new_appinsights_metric(client, appinsights_account):
    resp = client.get('/web/accounts/{}/tasks'.format(appinsights_account.id))

    assert resp.status_code == 200

@pytest.mark.usefixtures('authenticated_user')
def test_post_new_appinsights_metric(client, user, appinsights_account, faker):
    data = {
        'metric': 'requests/count',
        'nickname': faker.word(),
        'aggregation': 'count',

    }

    resp = client.post('/web/accounts/{}/tasks'.format(appinsights_account.id), data=data)

    assert resp.status_code == 302
    assert resp.headers['Location'].endswith('/web/accounts/')

    new_task = ApplicationInsightsMetricTask.query.filter_by(nickname=data['nickname']).one_or_none()
    assert new_task is not None
    assert new_task.metric == data['metric']
    assert new_task in appinsights_account.tasks
    assert new_task in user.tasks

