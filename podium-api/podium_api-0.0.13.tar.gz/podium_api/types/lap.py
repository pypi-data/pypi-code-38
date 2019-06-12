#!/usr/bin/env python
# -*- coding: utf-8 -*-
class PodiumLap(object):
    """
    Object that represents a Lap.

    **Attributes:**
        **uri** (str): Endpoint for accessing the lap.

         **raw_data_uri** (str): URI for accessing logged data.

         **lap_number** (str): Number for the lap.

         **end_time** (str): Time lap ended.

         **aggregates** (list): List of min/max/avg values for channels.

         **lap_time** (float): Lap time in minutes.

    """

    def __init__(self, uri, raw_data_uri, lap_number, end_time,
                 aggregates, lap_time):
        self.uri = uri
        self.raw_data_uri = raw_data_uri
        self.lap_number = lap_number
        self.end_time = end_time
        self.aggregates = aggregates
        self.lap_time = lap_time


def get_lap_from_json(json):
    """
    Returns a PodiumLap object from the json dict received from podium api.

    Args:
        json (dict): Dict of data from REST api

    Return:
        PodiumEvent: The PodiumEvent object for this data.
    """
    return PodiumLap(json["URI"], json["raw_data_uri"], json['lap_number'],
                     json['end_time'], json.get('aggregates', None),
                     json['lap_time'])
