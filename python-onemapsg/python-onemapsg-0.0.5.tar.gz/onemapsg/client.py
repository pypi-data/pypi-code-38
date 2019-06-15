# -*- coding: utf-8 -*-

"""
onemapsg.client
~~~~~~~~~~~~~~~

This module contains the OneMap SG Client.
"""

import inspect

from . import exceptions, status, utils
from .api import API
from .response import GeocodeInfo
from .utils import coerce_response, make_request


class OneMap:

    def __init__(self, email, password):
        self.token, self.token_expiry = self._connect(email, password)

    def _connect(self, email, password):
        """Retrieves token and stores it. Each token is valid
        for 3 days."""
        login_details = {'email': email, 'password': password}
        response = make_request(
            API.auth,
            method='post',
            data=login_details
        )
        if response.status_code == status.HTTP_200_OK:
            return (response.data['access_token'],
                    response.data['expiry_timestamp'])
        elif status.is_client_error(response.status_code):
            raise exceptions.AuthenticationError('Failed to authenticate.')
        elif status.is_server_error(response.status_code):
            raise exceptions.ServerError('OneMap SG server error. '
                                         'Please try again later.')

    def execute(self, action_type, *args, **kwargs):
        callback = getattr(utils, f'construct_{action_type}_query')
        url = callback(*args, **kwargs)
        response = make_request(url)
        if response.status_code == status.HTTP_200_OK:
            cls_callback = getattr(utils, f'get_{action_type}_class')
            cls = cls_callback()
            return coerce_response(cls, response.data)
        elif status.is_client_error(response.status_code):
            if 'error' in response.data:
                raise exceptions.BadRequest(response.data['error'])
            raise exceptions.BadRequest('Please ensure request is correct.')
        elif status.is_server_error(response.status_code):
            raise exceptions.ServerError('OneMap SG server error. '
                                         'Please try again later.')

    def search(self,
               search_val,
               return_geometry=True,
               get_address_details=True,
               page_number=None):
        """
        Returns search results with both latitude, longitude and x, y
        coordinates of the searched location.

        Ref: https://docs.onemap.sg/#search
        """
        name = inspect.stack()[0][3]
        return self.execute(name, search_val, return_geometry,
                            get_address_details, page_number)

    def route(self, start, end, route_type, public_transport_options=None):
        """
        Returns the distance and returns the drawn path between the specified
        start and end values depending on the route_type.

        Ref: https://docs.onemap.sg/#routing-service
        """
        name = inspect.stack()[0][3]
        return self.execute(name, start, end, route_type,
                            public_transport_options, self.token)

    def reverse_geocode(self,
                        reverse_type,
                        location,
                        buffer: int=10,
                        address_type: str='all',
                        other_features: bool=False) -> GeocodeInfo:
        """
        Retrieves a building address that lies within the defined buffer/radius of the specified x, y coordinates.

        Road names are returned within 20m of the specified coordinates in JSON format.

        Ref: https://docs.onemap.sg/#reverse-geocode-svy21
        """
        assert reverse_type in ['svy21', 'wgs84'], (
            '`reverse_type` can only be either `svy21` or `wgs84`.'
        )
        name = inspect.stack()[0][3]
        name = name + f'_{reverse_type}'
        return self.execute(name, location, self.token,
                            buffer, address_type,
                            other_features)
