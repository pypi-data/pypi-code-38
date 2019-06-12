#!/usr/bin/env python
# -*- coding: utf-8 -*-
class PodiumAlertMessage(object):
    """
    Object that represents an Alert Message

    **Attributes:**

        **alertmessage_id** (int): Id of alertmessage

        **send_time** (str): Time the message was sent. ISO 8601 format.

        **ack_time** (str): Time the message was acknowledged. ISO 8601 format.

        **message** (str): Message of the alert

        **priority** (int): Priority level of the message
        
        **sender_id** (int): Id of the alertmessage sender
        
        **eventdevice_uri:** (str): URI of the eventdevice this alertmessage belongs to
        
        **device_uri:** (str): URI of the device this alertmessage belongs to
        
        **user_uri** (str): URI of the user this alertmessage belongs to
    """
    def __init__(self, alertmessage_id, uri, send_time, ack_time, message, priority, sender_id, eventdevice_uri, device_uri, user_uri):
        self.alertmessage_id = alertmessage_id
        self.uri = uri
        self.send_time = send_time
        self.ack_time = ack_time
        self.message = message
        self.priority = priority
        self.sender_id = sender_id
        self.eventdevice_uri = eventdevice_uri
        self.device_uri = device_uri
        self.user_uri = user_uri

def get_alertmessage_from_json(json):
    """
    Returns an AlertMessage object from the json dict received from
    podium api.

    Args:
        json (dict): Dict of data from REST api

    Return:
        AlertMessage: The AlertMessage object for the data.
        
    """
    return PodiumAlertMessage(json['id'],
                        json['URI'],
                        json['send_time'],
                        json['ack_time'],
                        json['message'],
                        json['priority'],
                        json['sender_id'],
                        json['eventdevice_uri'],
                        json['device_uri'],
                        json['user_uri']
                        )
