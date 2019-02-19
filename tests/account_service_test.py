

def test_new_account(devops_account, token):
    assert devops_account.token != token