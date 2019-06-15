# -*- coding: utf-8 -*-

from onemapsg.api import API, BASE_URL, endpoints


def test_api_singleton():
    """API should prepend base URL to endpoint url."""
    for endpoint_name, endpoint_url in endpoints.items():
        assert getattr(API, endpoint_name) == f'{BASE_URL}{endpoint_url}'
