#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API classes to access beeswax monitoring information
"""
from __future__ import unicode_literals

import ujson

from beeswax_wrapper.core.base_classes import BaseAPI


class ActivityLog(BaseAPI):
    """Beeswax Activity Log API class"""

    paths = ['activity_log']

    def retrieve(self, log_id, **kwargs):
        """
        :type log_id: int
        :param dict kwargs: user_id, object_id, object_type, activity_date, action, details
        """
        parameters = dict(log_id=log_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: log_id, user_id, object_id, object_type, activity_date, action, details
        """
        return self._call('GET', data=ujson.dumps(kwargs))


class Alert(BaseAPI):
    """Beeswax Alert API class"""

    paths = ['alert']

    def retrieve(self, alert_id=None, **kwargs):
        """
        :type alert_id: int
        :param dict kwargs: user_id, subject, active, create_date, update_date
        """
        parameters = dict(alert_id=alert_id, **kwargs)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self, **kwargs):
        """
        :param dict kwargs: alert_id, user_id, subject, active, create_date, update_date
        """
        return self._call('GET', data=ujson.dumps(kwargs))

    def create(self, subject, content, from_address, **kwargs):
        """
        :type subject: str
        :type content: str
        :type from_address: str
        :param dict kwargs: user_id, account_id, object_type, object_id, is_global, icon, active
        """
        parameters = dict(subject=subject, content=content, from_address=from_address, **kwargs)
        return self._call('POST', data=ujson.dumps(parameters))

    def update(self, alert_id, **kwargs):
        """
        :type alert_id: int
        :param dict kwargs: user_id, is_global, active
        """
        parameters = dict(alert_id=alert_id, **kwargs)
        return self._call('PUT', data=ujson.dumps(parameters))

    def delete(self, alert_id):
        """
        :type alert_id: int
        """
        parameters = dict(alert_id=alert_id)
        return self._call('DELETE', data=ujson.dumps(parameters))


class Dashboard(BaseAPI):
    """Beeswax Dashboard API class"""

    paths = ['dashboard']

    def retrieve(self, dashboard):
        """
        :type dashboard: str
        """
        parameters = dict(dashboard=dashboard)
        return self._call('GET', data=ujson.dumps(parameters))[0]

    def list(self):
        return self._call('GET')
