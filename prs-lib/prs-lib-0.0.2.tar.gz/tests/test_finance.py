def test_get_wallet(client_with_auth):
    res = client_with_auth.finance.get_wallet()
    assert res.status_code == 200
    data = res.json()
    assert data and isinstance(data, dict)


def test_get_transactions(client_with_auth):
    res = client_with_auth.finance.get_transactions()
    assert res.status_code == 200
    data = res.json()
    assert data and isinstance(data, dict)


def test_recharge(client_with_auth):
    res = client_with_auth.finance.recharge(1)
    assert res.status_code == 200
    data = res.json()
    assert data and isinstance(data, dict)


def test_withdraw(client_with_auth):
    res = client_with_auth.finance.withdraw(1)
    assert res.status_code == 200
    data = res.json()
    assert data and isinstance(data, dict)
