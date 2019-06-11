# -*- coding: utf-8 -*-
from missinglink.sdk.sdk_version import get_version


def create_http_session():
    import requests

    session = requests.Session()

    session.headers.update({'User-Agent': 'ml-sdk/{}'.format(get_version())})

    return session
