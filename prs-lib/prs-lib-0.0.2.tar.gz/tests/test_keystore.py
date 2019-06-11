from . import DEV_USER, BETA_USER, PROD_USER


def test_get_by_email(client_without_auth):
    env = client_without_auth.config.env
    d = {
        'dev': DEV_USER,
        'beta': BETA_USER,
        'prod': PROD_USER,
    }
    email = d[env]['email']
    password = d[env]['password']
    res = client_without_auth.keystore.get_by_email(email, password)
    assert res.status_code == 200
    data = res.json()
    assert data['keystore']
