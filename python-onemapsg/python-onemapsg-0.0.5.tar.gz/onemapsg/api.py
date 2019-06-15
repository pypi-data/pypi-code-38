# -*- coding: utf-8 -*-

"""
onemapsg.api
~~~~~~~~~~~~

This module contains the static API endpoints of `OneMap SG`_.

.. _OneMap SG:
https://docs.onemap.sg/
"""

BASE_URL = 'https://developers.onemap.sg/'

endpoints = dict(
    auth='privateapi/auth/post/getToken',
    search='commonapi/search',
    route='privateapi/routingsvc/route',
    reverse_geocode='privateapi/commonsvc/revgeocodexy'
)


class APISingleton:
    """
    Maps endpoints into class attributes and prefixes the
    base URL.
    """

    def __init__(self):
        for k, v in endpoints.items():
            setattr(self, k, f'{BASE_URL}{v}')


API = APISingleton()
