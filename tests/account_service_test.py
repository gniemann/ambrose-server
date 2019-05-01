import pytest

from ambrose.models import ApplicationInsightsAccount, DevOpsAccount
from ambrose.services import DevOpsAccountService, ApplicationInsightsAccountService, AccountService


def test_new_account(devops_account, token):
    assert devops_account.token != token

@pytest.mark.parametrize('model, expected_service_type', [
    (DevOpsAccount, DevOpsAccountService),
    (ApplicationInsightsAccount, ApplicationInsightsAccountService)
])
def test_new_service(model, expected_service_type):
    service = AccountService(model())
    assert isinstance(service, expected_service_type)