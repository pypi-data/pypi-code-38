#!/usr/bin/env python
# -*- coding: utf-8 -*-

class PodiumToken(object):
    """
    A PodiumToken holds the OAuth2 Token for a logged in user.

    **Attributes:**
        **token** (string): The OAuth2 token for the user.

        **token_type** (string): The type of token issued.

        **created** (int): The time created.register_podium_application.
    """

    def __init__(self, token, token_type, created):
        self.token = token
        self.token_type = token_type
        self.created = created

def get_token_from_json(json):
    """
    Returns a PodiumToken object from the json dict received from podium api.

    Args:
        json (dict): Dict of data from REST api

    Return:
        PodiumToken: The PodiumToken object for the data.
    """
    return PodiumToken(json['access_token'], json['token_type'],
                       json['created_at'])
