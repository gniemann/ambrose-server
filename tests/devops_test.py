import pytest
from cryptography.fernet import Fernet

from config import Config
import devops_monitor


@pytest.fixture(scope='module')
def user(app):
    user = devops_monitor.models.User(username='test@test.com')
    devops_monitor.db.session.add(user)
    devops_monitor.db.session.commit()

    yield user

    devops_monitor.db.session.delete(user)

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