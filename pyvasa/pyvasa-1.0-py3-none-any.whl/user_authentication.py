#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author Hannes Ebelt <hannes.ebelt@sap.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

import requests
import os

from builtins import object
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
os.environ["CURL_CA_BUNDLE"] = ""


class UserAuthentication(object):
    token = None

    def __init__(self, url=None, port=None, vcenter_user=None, vcenter_password=None, api_version='1.0'):
        self.api = api_version
        self.port = port
        self.url = "https://" + url + ":" + self.port + "/api/rest/" + self.api + "/user/"
        self.vcenter_user = vcenter_user
        self.vcenter_password = vcenter_password

    def login(self):
        api_endpoint = "login"
        url_action = self.url + api_endpoint

        headers = {'Accept': 'application/json'}
        payload = {
            'vcenterPassword': self.vcenter_password,
            'vcenterUserName': self.vcenter_user
        }

        r = requests.post(url=url_action, headers=headers, json=payload)

        try:
            token = r.json()
        except ValueError:
            token = dict()

        token['status_code'] = r.status_code

        return token

    def logout(self, token=None):
        api_endpoint = "logout"
        url_action = self.url + api_endpoint
        headers = {
            'Accept': 'application/json',
            'vmware-api-session-id': token
        }

        r = requests.post(url=url_action, headers=headers, verify=False)

        try:
            out = r.json()
        except ValueError:
            out = dict()

        out['status_code'] = r.status_code

        return out
