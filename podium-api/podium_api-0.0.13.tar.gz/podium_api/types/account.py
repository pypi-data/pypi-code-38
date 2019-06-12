#!/usr/bin/env python
# -*- coding: utf-8 -*-

class PodiumAccount(object):
    """
    Object that represents a particular User.

    **Attributes:**
        **account_id** (str): Unique id for account

        **username** (string): The User's username.

        **email** (str): Account email address

        **user_uri** (str): URI to user associated with account

        **events_uri** (str): URI to account's events

        **devices_uri** (str): URI to account's devices

        **events_uri** (str): URI to account's events

        **streams_uri** (str): URI to account's current live streams

        **exports_uri** (str): URI to account's telemetry exports
    """

    def __init__(self, account_id, username, email, devices_uri, exports_uri,
                 streams_uri, user_uri, events_uri):
        self.account_id = account_id
        self.username = username
        self.email = email
        self.devices_uri = devices_uri
        self.exports_uri = exports_uri
        self.streams_uri = streams_uri
        self.user_uri = user_uri
        self.events_uri = events_uri


def get_account_from_json(json):
    """
    Returns a PodiumAccount object from the json dict received from podium api.

    Args:
        json (dict): Dict of data from REST api

    Return:
        PodiumUser: The PodiumAccount object for the data.
    """
    return PodiumAccount(json['id'], json['username'],
                         json['email'], json['devices_uri'],
                         json['exports_uri'], json['streams_uri'],
                         json['user_uri'], json['events_uri'])
