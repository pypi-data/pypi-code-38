#!/usr/bin/env python
# -*- coding: utf-8 -*-
class PodiumDevice(object):
    """
    Object that represents a Device.

    **Attributes:**
        **device_id** (str): Unique id for device.

        **uri** (str): Endpoint for accessing full device information.

        **serial** (str): Unique id for RaceCapture devices to identify
        themselves.

        **name** (str): Name of the device.

        **private** (bool): Is the event only viewable to creator?
    """

    def __init__(self, device_id, uri, serial, name, private):
        self.device_id = device_id
        self.uri = uri
        self.serial = serial
        self.name = name
        self.private = private


def get_device_from_json(json):
    """
    Returns a PodiumEvent object from the json dict received from podium api.

    Args:
        json (dict): Dict of data from REST api

    Return:
        PodiumEvent: The PodiumEvent object for this data.
    """
    return PodiumDevice(json['id'], json['URI'], json.get('serial', None),
                        json.get('name', None), json.get('private', None))
