# -*- coding: utf-8 -*-

"""
onemapsg.utils
~~~~~~~~~~~~~~

This module contains utilities shared across the package.
"""

from urllib.parse import urlencode

import requests

from onemapsg.api import API
from onemapsg.response import (
    GeocodeInfo, Response, RouteResult, SearchResult
)

SAFE_METHODS = ['get', 'options']


def to_dict(obj):
    """Converts class instances to dictionaries.
    Handles nested objects as well."""
    if not hasattr(obj, '__dict__'):
        return obj
    result = {}
    for key, val in obj.__dict__.items():
        element = []
        if not key.startswith('__'):
            if isinstance(val, list):
                for item in val:
                    element.append(to_dict(item))
            else:
                element = to_dict(val)
        result[key] = element
    return result


def make_request(endpoint, method='get',
                 data=None):
    """Makes a request to the given endpoint and maps the response
    to a Response class"""
    method = method.lower()
    request_method = getattr(requests, method)
    if method not in SAFE_METHODS and data is None:
        raise ValueError(
            'Data must be provided for POST, PUT and PATCH requests.'
        )
    if method not in SAFE_METHODS:
        r = request_method(endpoint, json=data)
    else:
        r = request_method(endpoint)
    return Response(status_code=r.status_code, data=r.json())


def construct_search_query(search_val, return_geometry,
                           get_address_details, page_number):
    """Constructs search query URL compliant with OneMap's requirements."""
    search_params = {
        'searchVal': search_val,
        'returnGeom': 'Y' if return_geometry else 'N',
        'getAddrDetails': 'Y' if get_address_details else 'N',
        'pageNum': page_number if page_number else 1
    }
    search_params = urlencode(search_params)
    search_url = f'{API.search}?{search_params}'
    return search_url


def get_search_class():
    """Returns SearchResult class."""
    return SearchResult


def validate_address_type(address_type: str) -> str:
    if address_type.lower() not in ['all', 'hdb']:
        raise ValueError(
            'Invalid `addressType` value - can only be `HDB` or `All`'
        )
    return address_type.lower()


def construct_reverse_geocode_svy21_query(location,
                                          token: str,
                                          buffer: int=10,
                                          address_type: str='all',
                                          other_features: bool=False) -> str:
    """Constructs Reverse Geocode (SVY21) query URL compliant with
    OneMap's requirements."""
    search_params = {
        'location': ','.join([str(loc).strip() for loc in location]),
        'token': token,
        'buffer': buffer,
        'addressType': validate_address_type(address_type),
        'otherFeatures': 'Y' if other_features else 'N'
    }
    search_params = urlencode(search_params, safe=',:-')
    search_url = f'{API.reverse_geocode}?{search_params}'
    return search_url


def get_reverse_geocode_svy21_class() -> GeocodeInfo:
    """Returns GeocodeInfo class."""
    return GeocodeInfo


construct_reverse_geocode_wgs84_query = construct_reverse_geocode_svy21_query
get_reverse_geocode_wgs84_class = get_reverse_geocode_svy21_class


def construct_route_query(start, end, route_type,
                          public_transport_options, token):
    """Constructs route query URL compliant with OneMap's requirements."""
    route_params = {
        'start': start,
        'end': end,
        'routeType': route_type
    }
    if route_type == 'pt' and public_transport_options:
        route_params.update(public_transport_options)
    route_params = urlencode(route_params, safe=',:-')
    route_url = f'{API.route}?{route_params}&token={token}'
    return route_url


def get_route_class():
    """Returns RouteResult class."""
    return RouteResult


def coerce_response(cls, data):
    """Creates a class object out of given response data and class."""
    return cls(**data)
