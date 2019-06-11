#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 3 19:29:03 2018

@author: patrickmcfarlane

event.py contains the Event class that
enables API calls for the events endpoints
"""

from .utils import api_video_call, parse_api_call

class Event:
    """ The Event class contains all resources needed to use the 
    event API calls. `stats.nba.com <https://stats.nba.com>`_
    has the following video-related API endpoints:

        - **events**: Game play-by-play video clips at the \
            play-level

    The Event class has the following required parameters:

        @param **game_id** (*str*): GameID in the API. 10-digit string \
            that represents a unique game. The format is two leading zeroes, \
            followed by a season indicator number ('1' for preseason, \
            '2' for regular season, '4' for the post-season), \
            then the trailing digits of the season in which the game \
            took place (e.g. '17' for the 2017-18 season). The following \
            5 digits increment from '00001' in order as the season progresses. \
            For example, '0021600001' is the **game_id** of the first game \
            of the 2016-17 NBA regular season.

        @param **season** (*str*): Season in the API. String of a two-year \
            season in a YYYY-ZZ format, where the ZZ are the last two \
            digits of the following year. For example, '2017-18' is a valid \
            value of **season** and represents the 2017-18 NBA season.

        @param **game_event_id** (*str*): GameEventID in the API. String of \
            an integer indicating the sequence of play-by-play events in a
            game, starting from 1.

    Attributes:

        **api_resp** (*dict*): JSON object of the API response. The API \
            response has three keys. The 'resource' key describes the \
            type of response returned ('events' in this instance). \
            The 'parameters' key describes the parameters provided in \
            the API call. The 'resultSets' key contains the data returned \
            in the API call.

        **data** (*dict*): A dictionary of response names. Each response \
            name is a key to a list of dictionaries containing the \
            corresponding data.
    """

    def __init__(self, headers, game_id, endpoint='events',
                 season='2017-18', game_event_id='154'):

        # Controlling the parameters depending on the endpoint
        params = {'GameID': game_id,
                  'Season': season,
                  'GameEventID': game_event_id,
                  'flag': '1'}

        self.api_resp = api_video_call(endpoint=endpoint,
                                       params=params,
                                       headers=headers)
