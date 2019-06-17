#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `nginxlib` package."""

from dateutil import parser
from urllib.parse import urlparse

import pytest  # noqa F401

from nginxlib import LogEntry


LOG_ENTRY = """
    96.49.212.83 - - [16/Jun/2019:22:52:21 +0000] "GET /vs/editor/editor.main.nls.js HTTP/1.1" 200 34027 "https://3000-98358490.staging-avl.appsembler.com/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:67.0) Gecko/20100101 Firefox/67.0" "-"  # noqa E503
    """


def test_get_event_time():
    """Given a log event string, I can get the time of the log event."""
    event_time = parser.parse("16/Jun/2019:22:52:21 +0000", fuzzy=True)

    event = LogEntry(LOG_ENTRY)

    assert event.timestamp == event_time


def test_get_url():
    """Given a log event string, I can get the url."""
    url_string = "https://3000-98358490.staging-avl.appsembler.com"
    url = urlparse(url_string)

    event = LogEntry(LOG_ENTRY)

    assert url == event.url


def test_get_deploy_id():
    """Given a log event string, I can get the deployment ID."""

    deploy_id = '98358490'

    event = LogEntry(LOG_ENTRY)

    assert deploy_id == event.deploy_id
