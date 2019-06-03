""" Utils for the python requests package
"""
import requests

from core_main_app.settings import SSL_CERTIFICATES_DIR


def send_get_request(url, params=None, **kwargs):
    """ Send a GET request using python requests.

    Args:
        url:
        params:
        **kwargs:

    Returns:

    """
    if 'verify' not in kwargs:
        kwargs['verify'] = SSL_CERTIFICATES_DIR
    return requests.get(url, params, **kwargs)


def send_post_request(url, data=None, json=None, **kwargs):
    """ Send a POST request using python requests.

    Args:
        url:
        data:
        json:
        **kwargs:

    Returns:

    """
    if 'verify' not in kwargs:
        kwargs['verify'] = SSL_CERTIFICATES_DIR
    return requests.post(url, data, json, **kwargs)

