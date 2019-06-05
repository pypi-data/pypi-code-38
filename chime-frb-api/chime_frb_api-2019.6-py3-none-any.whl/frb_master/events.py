#!/usr/bin/env python
# -*- coding: utf-8 -*-

from chime_frb_api.core import API


class Events(API):
    """
    CHIME/FRB Events API

    Attributes
    ----------
    base_url : str
        Base URL at which the is accessible.
    """

    def __init__(self, base_url: str = "http://frb-vsop.chime:8001"):
        API.__init__(self, base_url=base_url)

    def get_event(self, event_number: int = None):
        """
        Get CHIME/FRB Event Information

        Parameters
        ----------
        event_number : int
            CHIME/FRB Event Number

        Returns
        -------
            dict
        """
        if event_number is None:
            return "event_number is required."
        else:
            return self._get("/v1/events/{}".format(event_number))
