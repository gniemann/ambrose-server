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
    '/web/edit',
    '/web/accounts/',
    '/web/accounts/devops',
    '/web/accounts/application_insights',
    '/web/tasks/'
])
def test_index_authenticated(client, route, authenticated_user):
    resp = client.get(route)

    assert resp.status_code == 200