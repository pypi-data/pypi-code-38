#!/usr/bin/env python
# -*- coding: utf-8 -*-
from podium_api.types.event import get_event_from_json
from podium_api.types.friendship import get_friendship_from_json
from podium_api.types.user import get_user_from_json
from podium_api.types.eventdevice import get_eventdevice_from_json
from podium_api.types.device import get_device_from_json
from podium_api.types.lap import get_lap_from_json
from podium_api.types.venue import get_venue_from_json
from podium_api.types.alertmessage import get_alertmessage_from_json

class PodiumPagedResponse(object):
    """
    Object that represents data returned from a paged request.

    **Attributes:**
        **payload** (list): The data returned for this page.

        **total** (int): The total number of events found.

        **next_uri** (str): The URI for next page of results if available

        **prev_uri** (str): The URI for previous page of results if available

        **payload_name** (str): If a payload_name is provided attribute access
        on this name will also return the payload. Defaults to None. Used to
        mirror the web api.
    """

    def __init__(self, payload, total, next_uri, prev_uri, payload_name=None):
        self.payload = payload
        self.total = total
        self.next_uri = next_uri
        self.prev_uri = prev_uri
        self.payload_name = payload_name

    def __getattr__(self, name):
        if name == self.payload_name:
            return self.payload
        else:
            raise AttributeError()


PAYLOAD_NAME_TO_OBJECT = {
    'events': get_event_from_json,
    'friendships': get_friendship_from_json,
    'users': get_user_from_json,
    'eventdevices': get_eventdevice_from_json,
    'devices': get_device_from_json,
    'laps': get_lap_from_json,
    'venues': get_venue_from_json,
    'alertmessages': get_alertmessage_from_json,
}


def get_paged_response_from_json(json, payload_name):
    """
    Returns a PodiumPagedResponse object from the json dict received from
    podium api.

    Args:
        json (dict): Dict of data from REST api

        payload_name (str): Name of the actual paged data in the json dict.
        Will be used to determine the object the data gets converted into.
        The "payload" attr will also be returned with lookup by payload_name.

    Return:
        PodiumPagedResponse: The PodiumPagedResponse object for the data.
    """
    conversion_func = PAYLOAD_NAME_TO_OBJECT[payload_name]
    data = [conversion_func(x) for x in json[payload_name]]
    return PodiumPagedResponse(data, json['total'], json.get('nextURI', None),
                               json.get('prevURI', None),
                               payload_name=payload_name)
