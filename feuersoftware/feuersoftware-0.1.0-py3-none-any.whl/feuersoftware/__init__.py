#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import logging
import requests

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger("Feuersoftware API")

class PublicAPI(object):

    def __init__(self, token):
        self._headers = None
        self._headers = {
            'authorization': 'bearer {0}'.format(token),
            'accept': 'application/json',
            'content-type': 'application/json',
            }


    def get_operation(self):
        """Receive operation data."""
        self._url = "https://connectapi.feuersoftware.com/interfaces/public/operation"
        r = requests.get(self._url, headers=self._headers)
        if r.status_code != 200:
            _LOGGER.error("Error while sending API call 'get operation': {0} {1}".format(r.status_code, r.text))
        else:
            _LOGGER.info("Success, API call 'get operation' complete")
        return r


    def post_operation(self, start, keyword, update_strategy='none', **kwargs):
        """Start, update, cancel or close an operation. https://connectapi.feuersoftware.com/swagger/ui/index#!/Public32API/Public_PostOperation"""
        self._url = "https://connectapi.feuersoftware.com/interfaces/public/operation?updateStrategy={0}".format(update_strategy)
        valid_args = ("end", "status", "alarmenabled", "address", "position", "facts", "ric", "number", "properties")
        data = {"start": start, "keyword": keyword}
        for k, v in kwargs.items():
            if k in valid_args:
                data[k] = v
            else:
                _LOGGER.warning("Invalid argument passed to post_operation: {0}={1}".format(k, v))
        print(json.dumps(data))
        r = requests.post(self._url, data=json.dumps(data), headers=self._headers)
        if r.status_code != 204:
            _LOGGER.error("Error while sending API call 'post operation': {0} {1}".format(r.status_code, r.text))
        else:
            _LOGGER.info("Success, API call 'post operation' complete")
        return r


    def post_vehicle_status(self, radioid, status, **kwargs):
        """Set the status and position of a vehicle."""
        self._url = "https://connectapi.feuersoftware.com/interfaces/public/vehicle/{0}/status".format(radioid)
        valid_args = ("position")
        data = {"status": status}
        for k, v in kwargs.items():
            if k in valid_args:
                data[k] = v
            else:
                _LOGGER.warning("Invalid argument passed to post_vehicle_status: {0}={1}".format(k, v))
        r = requests.post(self._url, data=json.dumps(data), headers=self._headers)
        if r.status_code != 204:
            _LOGGER.error("Error while sending API call 'post vehicle status': {0} {1}".format(r.status_code, r.text))
        else:
            _LOGGER.info("Success, API call 'post vehicle status' complete")
        return r


    def post_user_status(self, username, status, **kwargs):
        """Set the status of a user regarding an operation."""
        self._url = "https://connectapi.feuersoftware.com/interfaces/public/operation/userstatus"
        valid_args = ("operationid")
        data = {"username": username, "status": status}
        for k, v in kwargs.items():
            if k in valid_args:
                data[k] = v
            else:
                _LOGGER.warning("Invalid argument passed to post_user_status: {0}={1}".format(k, v))
        r = requests.post(self._url, data=json.dumps(data), headers=self._headers)
        if r.status_code != 204:
            _LOGGER.error("Error while sending API call 'post user status': {0} {1}".format(r.status_code, r.text))
        else:
            _LOGGER.info("Success, API call 'post user status' complete")
        return r


    def get_alarmgroup(self):
        """Receive the usergroup of a user."""
        self._url = "https://connectapi.feuersoftware.com/interfaces/public/alarmgroup"
        r = requests.get(self._url, headers=self._headers)
        if r.status_code != 200:
            _LOGGER.error("Error while sending API call 'get alarmgroup': {0} {1}".format(r.status_code, r.text))
        else:
            _LOGGER.info("Success, API call 'get alarmgroup' complete")
        return r


    def put_alarmgroup(self, id, name, users):
        """Put a users into a alarmgroup."""
        self._url = "https://connectapi.feuersoftware.com/interfaces/public/alarmgroup/{0}".format(id)
        data = {"id":id, "name":name, "users":users}
        r = requests.put(self._url, data=json.dumps(data), headers=self._headers)
        if r.status_code != 200:
            _LOGGER.error("Error while sending API call 'put alarmgroup': {0} {1}".format(r.status_code, r.text))
        else:
            _LOGGER.info("Success, API call 'put alarmgroup' complete")
        return r


    def get_geocoding(self, address):
        """Receive geo coordinates for a given address."""
        self._url = "https://connectapi.feuersoftware.com/interfaces/public/geocoding"
        data = {"address": address}
        r = requests.get(self._url, data=json.dumps(data), headers=self._headers)
        if r.status_code != 200:
            _LOGGER.error("Error while sending API call 'get geocoding': {0} {1}".format(r.status_code, r.text))
        else:
            _LOGGER.info("Success, API call 'get geocoding' complete")
        return r


    def post_passwordcheck(self, password):
        """Let a password be checked."""
        self._url = "https://connectapi.feuersoftware.com/interfaces/public/passwordcheck"
        data = {"password": password}
        r = requests.post(self._url, data=json.dumps(data), headers=self._headers)
        if r.status_code != 200:
            _LOGGER.error("Error while sending API call 'post passwordcheck': {0} {1}".format(r.status_code, r.text))
        else:
            _LOGGER.info("Success, API call 'post passwordcheck' complete")
        return r


    def get_news(self):
        """Receive news."""
        self._url = "https://connectapi.feuersoftware.com/interfaces/public/news"
        r = requests.get(self._url, headers=self._headers)
        if r.status_code != 200:
            _LOGGER.error("Error while sending API call 'get news': {0} {1}".format(r.status_code, r.text))
        else:
            _LOGGER.info("Success, API call 'get news' complete")
        return r


    def post_news(self, title, content, start, end, **kwargs):
        """Create a news entry."""
        self._url = "https://connectapi.feuersoftware.com/interfaces/public/news"
        valid_args = ("groups", "mailinglists", "site")
        data = {"title": title, "content": content, "start": start, "end": end}
        for k, v in kwargs.items():
            if k in valid_args:
                data[k] = v
            else:
                _LOGGER.warning("Invalid argument passed to post_news: {0}={1}".format(k, v))
        r = requests.post(self._url, data=json.dumps(data), headers=self._headers)
        if r.status_code != 200:
            _LOGGER.error("Error while sending API call 'post news': {0} {1}".format(r.status_code, r.text))
        else:
            _LOGGER.info("Success, API call 'post news' complete")
        return r


    def delete_news(self, id):
        """Delete news."""
        self._url = "https://connectapi.feuersoftware.com/interfaces/public/news/{0}".format(id)
        r = requests.delete(self._url, headers=self._headers)
        if r.status_code != 204:
            _LOGGER.error("Error while sending API call 'delete news': {0} {1}".format(r.status_code, r.text))
        else:
            _LOGGER.info("Success, API call 'delete news' complete")
        return r


    def put_news(self, id, title, content, start, end, **kwargs):
        """Update a news entry."""
        self._url = "https://connectapi.feuersoftware.com/interfaces/public/news/{0}".format(id)
        valid_args = ("groups", "mailinglists", "site")
        data = {"title": title, "content": content, "start": start, "end": end}
        for k, v in kwargs.items():
            if k in valid_args:
                data[k] = v
            else:
                _LOGGER.warning("Invalid argument passed to put_news: {0}={1}".format(k, v))
        r = requests.put(self._url, data=json.dumps(data), headers=self._headers)
        if r.status_code != 200:
            _LOGGER.error("Error while sending API call 'put news': {0} {1}".format(r.status_code, r.text))
        else:
            _LOGGER.info("Success, API call 'put news' complete")
        return r


