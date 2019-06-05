#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Core API Class Object
"""

import requests


class API(object):
    """
    Application Programming Interface Base Class
    """

    def __init__(self, base_url: str = None):
        """
        API Initialization

        Parameters
        ----------
        base_url : str
            Base url for API
        """
        self.base_url = base_url

    def _post(self, url, payload):
        """
        HTTP Post

        Parameters
        ----------
        url : str
            HTTP Url
        payload : JSON Encodeable
            Post Payload

        Returns
        -------
        response : json

        Raises
        ------
        requests.exceptions.RequestException
        """
        try:
            response = requests.post(self.base_url + url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise e

    def _get(self, url):
        try:
            response = requests.get(self.base_url + url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise e

    def _delete(self, url):
        try:
            response = requests.delete(self.base_url + url)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise e
