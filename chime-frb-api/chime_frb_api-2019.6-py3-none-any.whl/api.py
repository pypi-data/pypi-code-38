#!/usr/bin/env pythonAAOA
# -*- coding: utf-8 -*-

import requests


class API(object):
    """
    Application Programming Interface Base Class
    """

    def __init__(self, base_url: str = None):
        self.base_url = base_url

    def _post(self, url, payload):
        try:
            response = requests.post(self.base_url + url, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise e

    def _get(self, url):
        try:
            response = requests.get(self.base_url + url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise e

    def _delete(self, url):
        try:
            response = requests.delete(self.base_url + url)
            response.raise_for_status()
            return response
        except Exception as e:
            raise e
