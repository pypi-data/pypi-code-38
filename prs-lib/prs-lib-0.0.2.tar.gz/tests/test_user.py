from . import now_str, AVATAR_BASE64_STR


def test_get_by_address(client_with_auth):
    user_address = client_with_auth.config.address
    res = client_with_auth.user.get_by_address(user_address)
    assert res.status_code == 200
    data = res.json()
    assert data and isinstance(data, dict)


def test_edit_profile(client_with_auth):
    profile = {
        'name': 'presson test %s' % now_str(),
        'title': 'test title',
    }
    res = client_with_auth.user.edit_profile(profile)
    assert res.status_code == 200
    data = res.json()
    assert data and isinstance(data, dict)


def test_upload_avatar(client_with_auth):
    res = client_with_auth.user.upload_avatar(AVATAR_BASE64_STR)
    assert res.status_code == 200
    data = res.json()
    assert data and isinstance(data, dict)
