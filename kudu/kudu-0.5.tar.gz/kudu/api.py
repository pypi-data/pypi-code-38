import requests

api_url = 'https://api.pitcher.com'
pitcher_file_categories = ['presentation', 'zip', 'interface']


def request(method, url, token=None, **kwargs):
    return getattr(requests, method)(
        api_url + url,
        headers={'Authorization': 'Token %s' % token} if token else None,
        **kwargs
    )


def authenticate(username, password):
    res = request('post', '/auth/user/', json={
        'username': username,
        'password': password
    })

    if res.status_code != 200:
        raise ValueError

    return res.json().get('token')
