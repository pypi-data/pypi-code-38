#!/usr/bin/env python
# -*- coding: utf-8 -*-
class PodiumFriendship(object):
    """
    Object that represents a Friendship

    **Attributes:**

        **friendship_id** (int): Integer Id of the friendship

        **user_id** (int): Integer id for user following the friend

        **user_uri** (str): URI to user following the friend.

        **friend_id** (int): Integer id for the user being followed.

        **friend_uri** (str): URI to user being followed.

    """
    def __init__(self, friendship_id, user_id, user_uri, friend_id,
                 friend_uri):
        self.friendship_id = friendship_id
        self.user_id = user_id
        self.user_uri = user_uri
        self.friend_id = friend_id
        self.friend_uri = friend_uri


def get_friendship_from_json(json):
    """
    Returns a PodiumFriendship object from the json dict received from
    podium api.

    Args:
        json (dict): Dict of data from REST api

    Return:
        PodiumFriendship: The PodiumFriendship object for the data.

    """
    return PodiumFriendship(json['id'], json['user_id'],
                            json['user_uri'], json['friend_id'],
                            json['friend_uri'])
