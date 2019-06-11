from . import now_str

import prs_utility as utility

DAPP_NAME = None
APP_ADDRESS = None
APP_PRIVATE_KEY = None
CODE = None


def get_dapp_name():
    return f'Test APP {now_str()}'


def test_name_not_exist(client_with_auth):
    dapp_name = get_dapp_name()
    # check if exist by dapp name
    res = client_with_auth.dapp.is_name_exist(dapp_name)
    assert res.status_code == 200
    data = res.json()
    assert data['isExist'] is False


def create_dapp(c):
    dapp_name = get_dapp_name()
    # create dapp
    dapp = {
        'name': dapp_name,
        'description': 'This is a testing app.',
        'url': 'http://xx.com',
        'redirect_url': f'{c.config.host}/auth',
    }
    res = c.dapp.create(dapp)
    assert res.status_code == 200
    data = res.json()
    app_address = data['address']
    assert app_address
    return dapp_name, app_address


def test_create_dapp(client_with_auth):
    global DAPP_NAME, APP_ADDRESS
    DAPP_NAME, APP_ADDRESS = create_dapp(client_with_auth)
    # check if exist by dapp name
    res = client_with_auth.dapp.is_name_exist(DAPP_NAME)
    assert res.status_code == 200
    data = res.json()
    assert data and isinstance(data, dict)
    assert data['isExist'] is True


def test_update_dapp(client_with_auth):
    dapp_name = get_dapp_name()
    dapp = {
        'name': dapp_name,
        'description': f'update description for {dapp_name}',
        'url': 'http://xx.com',
        'redirect_url': f'{client_with_auth.config.host}/auth',
    }
    global APP_ADDRESS
    res = client_with_auth.dapp.update(APP_ADDRESS, dapp)
    data = res.json()
    APP_ADDRESS = data['address']
    assert APP_ADDRESS
    assert data['name'] == dapp['name']
    assert data['description'] == dapp['description']


def test_delete_dapp(client_with_auth):
    global APP_ADDRESS
    res = client_with_auth.dapp.delete(APP_ADDRESS)
    assert res.status_code == 400
    data = res.json()
    assert data['code'] == 'ERR_APP_CAN_NOT_BE_DELETED'


def test_recreate_dapp(client_with_auth):
    global DAPP_NAME, APP_ADDRESS
    DAPP_NAME, APP_ADDRESS = create_dapp(client_with_auth)
    # check if exist by dapp name
    res = client_with_auth.dapp.is_name_exist(DAPP_NAME)
    assert res.status_code == 200
    data = res.json()
    assert data and isinstance(data, dict)
    assert data['isExist'] is True


def test_get_dapp_by_address(client_with_auth):
    global APP_ADDRESS
    # get dapp by address
    res = client_with_auth.dapp.get_by_address(APP_ADDRESS)
    assert res.status_code == 200
    data = res.json()
    global APP_PRIVATE_KEY
    APP_PRIVATE_KEY = data['privateKey']
    assert APP_PRIVATE_KEY


def test_get_apps(client_with_auth):
    # get dapps
    res = client_with_auth.dapp.get_dapps()
    assert res.status_code == 200


def test_get_authorize_url(client_with_auth):
    global APP_ADDRESS
    auth_url = client_with_auth.dapp.get_authorize_url(APP_ADDRESS)
    assert auth_url


def test_web_authorize(client_buyer):
    global APP_ADDRESS
    res = client_buyer.dapp.web_authorize(APP_ADDRESS)
    assert res.status_code == 200
    data = res.json()
    global CODE
    CODE = data['code']
    assert CODE


def test_auth_by_code(client_with_auth):
    global CODE, APP_ADDRESS, APP_PRIVATE_KEY
    res = client_with_auth.dapp.auth_by_code(
        CODE, APP_ADDRESS, APP_PRIVATE_KEY
    )
    assert res.status_code == 200


def test_authenticate(client_with_auth):
    global APP_ADDRESS, KEY_PAIR
    KEY_PAIR = utility.create_key_pair()
    # authenticate
    res = client_with_auth.dapp.authenticate(APP_ADDRESS, KEY_PAIR['address'])
    assert res.status_code == 200


def test_deauthenticate(client_with_auth):
    global APP_ADDRESS, KEY_PAIR
    res = client_with_auth.dapp.deauthenticate(
        APP_ADDRESS, KEY_PAIR['address']
    )
    assert res.status_code == 200


def test_delete_dapp(client_with_auth):
    global APP_ADDRESS
    res = client_with_auth.dapp.delete(APP_ADDRESS)
    assert res.status_code == 400
    data = res.json()
    assert data['code'] == 'ERR_APP_CAN_NOT_BE_DELETED'
