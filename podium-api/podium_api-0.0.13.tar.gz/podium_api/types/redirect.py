#!/usr/bin/env python
# -*- coding: utf-8 -*-
class PodiumRedirect(object):
    """
    Object representing the redirect return from the podium api.

    **Attributes:**
        **location** (str): URI for the redirected object.

        **type** (str): Type of object. Can be 'event', 'device', 'eventdevice'
    """
    def __init__(self, location, object_type):
        self.location = location
        self.object_type = object_type


def get_redirect_from_json(json, object_type):
    """
    Returns a PodiumRedirect object from the provided json dict.

    Args:
        json (dict): Dict of data from REST api

        object_type (str): The type of object this redirect URI represents.

    Return:
        PodiumRedirect: The PodiumRedirect object for this data.
    """
    return PodiumRedirect(json['location'], object_type)
