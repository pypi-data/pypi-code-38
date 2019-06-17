#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API classes to access beeswax account information
"""
from __future__ import unicode_literals

import ujson

from beeswax_wrapper.core.base_classes import BaseAPI


class Account(BaseAPI):
    """Beeswax Account API class"""

    paths = ['account']

    def __init__(self, *args, **kwargs):
        super(Account, self).__init__(*args, **kwargs)
        self.alerts = AccountAlert(self._dal)
        self.settings = AccountSetting(self._dal)

    def retrieve(self, account_id, **kwargs):
        """
        :type account_id: int
        :param dict kwargs: customer_id, alternative_id, account_name, primary_account, active, create_date, update_date
        """
        parameters = dict(account_id=account_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: account_id, customer_id, alternative_id, account_name, primary_account, active, create_date,
            update_date
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, account_name, **kwargs):
        """
        :type account_name: str
        :param dict kwargs: customer_id, alternative_id, primary_account, locale, timezone, currency_id,
            date_format_string, notes
        """
        parameters = dict(account_name=account_name, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, account_id, **kwargs):
        """
        :type account_id: int
        :param dict kwargs: customer_id, alternative_id, account_name, primary_account, locale, timezone, currency_id,
            date_format_string, notes, active
        """
        parameters = dict(account_id=account_id, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))


class AccountAlert(BaseAPI):
    """Beeswax Account Alert API class"""

    paths = ['account_alert']

    def create(self, system_alert_key, **kwargs):
        """
        :type system_alert_key: str|int
        :param dict kwargs: email, slack_api, slack_channel, slack_emoji, active
        """
        parameters = dict(system_alert_key=system_alert_key, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, account_alert_id, **kwargs):
        """
        :type account_alert_id: int
        :param dict kwargs: system_alert_key, email, slack_api, slack_channel, slack_emoji, active
        """
        parameters = dict(account_alert_id=account_alert_id, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))

    def delete(self, account_alert_id):
        """
        :type account_alert_id: int
        """
        parameters = dict(account_alert_id=account_alert_id)
        return self._call('DELETE', data=ujson.dumps(parameters))


class AccountSetting(BaseAPI):
    """Beeswax Account Setting API class"""

    paths = ['account_setting']

    def retrieve(self, as_id, **kwargs):
        """
        :type as_id: int
        :param dict kwargs: account_setting
        """
        parameters = dict(as_id=as_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: as_id, account_setting
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, account_setting, value):
        """
        :type account_setting: str|int
        :type value: str|int|float
        """
        parameters = dict(account_setting=account_setting, value=value)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, as_id, account_setting, value):
        """
        :type as_id: int
        :type account_setting: str|int
        :type value: str|int|float
        """
        parameters = dict(as_id=as_id, account_setting=account_setting, value=value)
        return self._call('PUT', data=ujson.dumps(parameters))

    def delete(self, as_id):
        """
        :type as_id: int
        """
        parameters = dict(as_id=as_id)
        return self._call('DELETE', data=ujson.dumps(parameters))
