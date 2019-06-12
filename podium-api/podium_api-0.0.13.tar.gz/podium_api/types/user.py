#!/usr/bin/env python
# -*- coding: utf-8 -*-

class PodiumUser(object):
    """
    Object that represents a particular User.

    **Attributes:**
        **user_id** (int): User id

        **uri** (string): URI for the User.

        **username** (string): The User's username.

        **description** (string): The User's description.

        **avatar_url** (string): User's avatar image url.

        **links** (list): 3rd party links for the user.

        **friendships_uri** (string): URI to friends list.

        **followers_uri** (string): URI to followers list.

        **friendship_uri** (string): If this User has been friended
        
        **events_uri** (string): URI to events for this user
        
        **venues_uri** (string): URI to venues this user particiated at
         
        by the user this attr will have a value, otherwise None. Defaults to
        None.
    """
    def __init__(self, user_id, uri, username, description, avatar_url, profile_image_url,
                 links, friendships_uri, followers_uri, friendship_uri, events_uri,
                 venues_uri):
        self.user_id = user_id
        self.uri = uri
        self.username = username
        self.description = description
        self.avatar_url = avatar_url
        self.profile_image_url = profile_image_url
        self.links = links
        self.friendships_uri = friendships_uri
        self.followers_uri = followers_uri
        self.friendship_uri = friendship_uri
        self.events_uri = events_uri
        self.venues_uri = venues_uri


def get_user_from_json(json):
    """
    Returns a PodiumUser object from the json dict received from podium api.

    Args:
        json (dict): Dict of data from REST api

    Return:
        PodiumUser: The PodiumUser object for the data.
    """
    return PodiumUser(json['id'],
                      json['URI'],
                      json['username'],
                      json['description'],
                      json['avatar_url'],
                      json['profile_image_url'],
                      json['links'],
                      json['friendships_uri'],
                      json['followers_uri'],
                      json.get("friendship_uri", None),
                      json['events_uri'],
                      json['venues_uri']
                      )
