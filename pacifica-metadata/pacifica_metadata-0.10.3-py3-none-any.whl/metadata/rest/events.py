#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Emit events for different things."""
from datetime import datetime
import logging
from json import dumps
import requests
from requests import RequestException
from ..config import get_config


def emit_event(**kwargs):
    """Emit a cloud event that the data is now accepted."""
    try:
        resp = requests.post(
            get_config().get('notifications', 'url'),
            data=dumps({
                'cloudEventsVersion': '0.1',
                'eventType': kwargs.get('eventType'),
                'source': kwargs.get('source'),
                'eventID': kwargs.get('eventID'),
                'eventTime': datetime.now().replace(microsecond=0).isoformat(),
                'extensions': kwargs.get('extensions', {}),
                'contentType': 'application/json',
                'data': kwargs.get('data', {})
            }),
            headers={'Content-Type': 'application/json'}
        )
        resp_major = int(int(resp.status_code)/100)
        assert resp_major == 2
    except (RequestException, AssertionError) as ex:
        logging.warning('Unable to send notification: %s', ex)
