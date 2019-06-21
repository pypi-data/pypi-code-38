#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from API_callers.base import Singleton
import requests
import logging


class APIUser(metaclass=Singleton):
    def __init__(self, url_login_api, login_payload):
        self.login_url = url_login_api
        self.payload = login_payload

    @property
    def response(self):
        response = requests.post(self.login_url, json=self.payload)
        return response

    @property
    def _token(self):
        try:
            _json = self.response.json()
            return _json
        except Exception as e:
            logging.error('Error on APIUser:\n {}'.format(e))
            return None

    def get_token(self):
        return self._token
