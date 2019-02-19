import pytest

import devops_monitor


@pytest.fixture()
def authenticated_user(user):
    @devops_monitor.login_manager.request_loader
    def load_user_from_request(request):
        return user
        

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
    '/web/messages/new/text',
    '/web/messages/new/datetime',
    '/web/messages/new/task',
    '/web/edit',
    '/web/accounts/',
    '/web/accounts/devops',
    '/web/accounts/application_insights',
    '/web/tasks/'
])
def test_index_authenticated(client, route, authenticated_user):
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