#!/usr/bin/env python
# -*- coding: utf-8 -*-

class PodiumVenue(object):
    """
    Object that represents a Venue.

    **Attributes:**
        **venue_id** (int): Venue Id

        **uri** (string): URI for the Venue.

        **name** (string): The Venue's name.
    """
    def __init__(self, venue_id, uri, events_uri, updated, created,
                 name,
                 centerpoint,
                 country_code,
                 configuration,
                 track_map_array,
                 start_finish,
                 finish,
                 sector_points,
                 length
                 ):
        self.venue_id = venue_id
        self.uri = uri
        self.events_uri = events_uri
        self.updated = updated
        self.created = created
        self.name = name
        self.centerpoint = centerpoint
        self.country_code = country_code
        self.configuration = configuration
        self.track_map_array = track_map_array
        self.start_finish = start_finish
        self.finish = finish
        self.sector_points = sector_points
        self.length = length

def get_venue_from_json(json):
    """
    Returns a PodiumVenue object from the json dict received from podium api.

    Args:
        json (dict): Dict of data from REST api

    Return:
        PodiumVenue: The PodiumVenue object for the data.
    """
    return PodiumVenue(json['id'],
                      json['URI'],
                      json['events_uri'],
                      json['updated'],
                      json['created'],
                      json.get('name', None),
                      json.get('centerpoint', None),
                      json.get('country_code', None),
                      json.get('configuration', None),
                      json.get('track_map_array', None),
                      json.get('start_finish', None),
                      json.get('finish', None),
                      json.get('sector_points', None),
                      json.get('length', None)
                      )
