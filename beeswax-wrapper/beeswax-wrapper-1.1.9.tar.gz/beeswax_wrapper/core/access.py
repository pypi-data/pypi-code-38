#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Beeswax specific access classes for the wrapper
"""
from __future__ import unicode_literals

import logging
import traceback
import ujson

import requests
from requests import ConnectionError

from beeswax_wrapper.core.exceptions import BeeswaxRESTException
from beeswax_wrapper.credentials.credential_manager import get_beeswax_credentials
from beeswax_wrapper.modules import account, admin, creatives, extensions, monitoring, operations, segments


try:
    unicode = unicode
except NameError:  # 2to3
    unicode = str


BEESWAX_DAL = None


class BeeswaxDAL(object):
    """
    DAL specific to beeswax
    Creates a session and authenticates it using the beeswax authentication endpoint
    """

    def __init__(self, endpoint_url):
        self.endpoint_url = endpoint_url
        self._session = None

    @property
    def session(self):
        """
        Get or create a requests Session
        :rtype: requests.Session
        """
        if not self._session:
            self._session = requests.Session()
        return self._session

    def _call(self, method, paths, **kwargs):
        """
        returns the results of an endpoint _call
        :rtype: list|dict
        """
        if self.endpoint_url is None:
            raise RuntimeError('Must provide a valid endpoint_url as str|unicode')

        url = self.endpoint_url + '/'.join(map(unicode, paths))

        call_func = getattr(self.session, method.lower())
        response = call_func(url, **kwargs).json()

        if isinstance(response, list):
            return response

        if not response['success']:
            raise BeeswaxRESTException('\n'.join(response.get('errors', [response.get('message', '')])))

        return response.get('payload')

    def authenticate(self, username=None, password=None):
        """
        Authenticates the user credentials provided
        :type username: str
        :type password: str
        :rtype: list|dict
        """
        return self.masquerade(username, password)

    def masquerade(self, username=None, password=None, account_id=None):
        """
        Changes the user account_id
        :type username: str
        :type password: str
        :type account_id: int
        :rtype: list|dict
        """
        if not (username and password):
            credentials = get_beeswax_credentials()
            username = username or credentials['username']
            password = password or credentials['password']

        parameters = {'email': username, 'password': password}
        if account_id:
            parameters['account_id'] = account_id

        return self._call('POST', ['authenticate'], data=ujson.dumps(parameters))

    def call(self, method, paths, **kwargs):
        """
        returns the results of an endpoint _call
        auto authenticates if connections go stale
        :rtype: requests.Response
        """
        try:
            return self._call(method, paths, **kwargs)
        except (ConnectionError, BeeswaxRESTException):  # connection timed out or not authenticated
            logging.warning(traceback.format_exc())
            self.authenticate()
            return self.call(method, paths, **kwargs)


def get_beeswax_dal():
    """
    'Singleton' beeswax DAL.
    All beeswax API's share the same DAL connection per process
    dependency injection example
    """
    global BEESWAX_DAL
    if BEESWAX_DAL is None:
        BEESWAX_DAL = BeeswaxDAL(None)
    return BEESWAX_DAL


def configure_endpoint(url):
    get_beeswax_dal().endpoint_url = url


class BeeswaxAPI(object):
    """Beeswax API for communicating with the beeswax interface"""

    def __init__(self, username=None, password=None):
        self.dal = get_beeswax_dal()

        self.accounts = account.Account(self.dal)

        self.authentication = admin.Authentication(self.dal)
        self.passwords = admin.Password(self.dal)
        self.roles = admin.Role(self.dal)
        self.users = admin.User(self.dal)

        self.creatives = creatives.Creative(self.dal)

        self.bid_modifiers = extensions.BidModifier(self.dal)
        self.custom_lists = extensions.CustomList(self.dal)
        self.list_items = extensions.ListItem(self.dal)
        self.native_offers = extensions.NativeOffer(self.dal)
        self.push_queue = extensions.PushQueue(self.dal)
        self.reports = extensions.Report(self.dal)
        self.strategies = extensions.Strategy(self.dal)
        self.targeting_templates = extensions.TargetingTemplate(self.dal)
        self.vendors = extensions.Vendor(self.dal)
        self.misc = extensions.Misc(self.dal)

        self.activity_logs = monitoring.ActivityLog(self.dal)
        self.alerts = monitoring.Alert(self.dal)
        self.dashboards = monitoring.Dashboard(self.dal)

        self.advertisers = operations.Advertiser(self.dal)
        self.campaigns = operations.Campaign(self.dal)
        self.events = operations.Event(self.dal)
        self.line_items = operations.LineItem(self.dal)

        self.segments = segments.Segment(self.dal)
        self.segment_categories = segments.SegmentCategory(self.dal)

        if username or password:
            self.change_user(username, password)

    def change_user(self, username, password):
        """Change the sessions user cookies"""
        self.dal.authenticate(username, password)

    def masquerade(self, account_id=None):
        self.dal.masquerade(account_id=account_id)
