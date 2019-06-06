# -*- coding: utf-8 -*-
#
# name:             zone.py
# author:           Harold Bradley III | Prestix Studio, LLC.
# email:            harold@prestix.studio
# created on:       09/15/2018
#

"""
cloudns_api.zone
~~~~~~~~~~~~~~~~

This module contains API wrapper functions for listing, creating, updating,
and deleting zones.
"""

import requests

from .api import api, patch_update
from .parameters import Parameters


@api
def list(page=1, rows_per_page=30, search=''):
    """Returns a paginated list of zones

    :param page: (optional) int, current page
    :param rows_per_page: (optional) int, number of results on each page
    :param search: (optional) string used to search domain names, reverse zone
        name, or other keyword to search for in the zone names
    """
    url = 'https://api.cloudns.net/dns/list-zones.json'

    params = Parameters({
            'page'          : page,
            'rows-per-page' : rows_per_page,
            'search' : {
                'value'     : search,
                'optional'  : True,
            },
        })

    return requests.get(url, params=params.to_dict())


@api
def get_page_count(rows_per_page=30, search=''):
    """Returns the number of pages for the full listing or search listing

    :param rows_per_page: int, number of results on each page
    :param search: (optional) string used to search domain names, reverse zone
        name, or other keyword to search for in the zone names
    """
    url = 'https://api.cloudns.net/dns/get-pages-count.json'

    params = Parameters({
            'rows-per-page' : {
                'value'  : rows_per_page,
                # only certain values allowed.
                # in both places
            },
            'search' : {
                'value'     : search,
                'optional'  : True,
            },
        })

    return requests.get(url, params=params.to_dict())


@api
def create():
    """Creates a new DNS zone.

    :param page: (optional) int, current page
    :param rows_per_page: (optional) int, number of results on each page
    :param search: (optional) string used to search domain names, reverse zone
        name, or other keyword to search for in the zone names
    """
    url = 'https://api.cloudns.net/dns/register.json'

    params = Parameters({
            'rows-per-page' : rows_per_page,
            'search' : {
                'value'     : search,
                'optional'  : True,
            },
        })

    return requests.post(url, params=params.to_dict())
