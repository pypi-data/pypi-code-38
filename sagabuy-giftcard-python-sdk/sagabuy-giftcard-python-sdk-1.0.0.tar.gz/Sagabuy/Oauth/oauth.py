#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from urllib import request
from urllib.request import urlopen
from urllib import parse

class Oauth:

    def __init__(self, config):
        self.app_id = config.get_app_id()
        self.app_secret = config.get_app_secret()
        self.url = config.get_request_url()

    def get_token(self):
        params = {
            'client_id': self.app_id,
            'client_secret': self.app_secret
        }
        data = parse.urlencode(params).encode("utf-8")
        return self.post(data)

    def post(self, data):
        try:
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
            }
            req_url = self.url + 'oauth'
            req = request.Request(req_url, data, headers)
            res = urlopen(req)
            return json.loads(res.read().decode("utf-8"))
        except Exception as e:
            raise Exception('sagabuy api response:{}'.format(e))