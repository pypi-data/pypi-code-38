#!/usr/bin/env python
# -*- coding: utf-8 -*-
class PodiumEvent(object):
    """
    Object that represents an Event.

    **Attributes:**
        **event_id** (str): Unique id for event

        **uri** (str): Endpoint for accessing full event information.

        **devices_uri** (str): Endpoint for accessing devices that 
        attended the event.

        **title** (str): Title of Event

        **start_time** (str): Start time of the event. ISO 8601 format.

        **end_time** (str): End time of the event. ISO 8601 format.

        **venue_uri** (str): Endpoint for accessing venue information.

        **private** (bool): Is the event only viewable to creator?
        
        **user_uri** (str): Endpoint for accessing user information
        
        **user_avatar_url** (str): URL for user avatar
    """

    def __init__(self, event_id, uri, devices_uri, title, start_time,
                 end_time, venue_uri, venue_id, private, user_uri, user_avatar_url):
        self.event_id = event_id
        self.uri = uri
        self.devices_uri = devices_uri
        self.title = title
        self.start_time = start_time
        self.end_time = end_time
        self.venue_uri = venue_uri
        self.venue_id = venue_id
        self.private = private
        self.user_uri = user_uri
        self.user_avatar_url = user_avatar_url


def get_event_from_json(json):
    """
    Returns a PodiumEvent object from the json dict received from podium api.

    Args:
        json (dict): Dict of data from REST api

    Return:
        PodiumEvent: The PodiumEvent object for this data.
    """
    return PodiumEvent(json['id'], json['URI'], json.get('devices_uri', None),
                       json.get('title', None), json.get('start_time', None),
                       json.get('end_time', None),
                       json.get('venue_uri', None), json.get('venue_id', None),
                       json.get('private', None),
                       json.get('user_uri', None), json.get('user_avatar_url', None))
