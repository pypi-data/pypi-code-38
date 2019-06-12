#!/usr/bin/env python
# -*- coding: utf-8 -*-

class PodiumApplication():

    def __init__(self, app_id, app_secret, podium_url=None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.podium_url = 'https://podium.live' if podium_url is None else podium_url
