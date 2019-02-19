import pytest
from cryptography.fernet import Fernet

from devops_monitor.models import DevOpsAccount, db
from devops_monitor.services import DevOpsAccountService

@pytest.fixture(scope='module')
def token(faker):
    return faker.sha1()

@pytest.fixture(scope='module')
def cipher():
    return Fernet(Fernet.generate_key())

@pytest.fixture(scope='module')
def devops_account(user, faker, token, cipher):
    account = DevOpsAccountService(cipher).new_account(
        user,
        faker.email(),
        faker.word(),
        token,
        faker.word()
    )

    yield account

    db.session.delete(account)
    db.session.commit()


def test_new_account(devops_account, token):
    assert devops_account.token != token