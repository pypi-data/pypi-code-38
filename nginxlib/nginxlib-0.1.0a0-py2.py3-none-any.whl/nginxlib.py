# -*- coding: utf-8 -*-
"""
Utilities to parse nginx logs.
"""

from dateutil import parser
import re
from urllib.parse import urlparse

from .exceptions import DateNotFound, URINotFound


def extract_timestamp(log_entry):
    """Given a log entry, return a Python object
    (datetime.datetime) from the timestamp."""
    pattern = r"\[(.+)\]\s"
    match = re.search(pattern, log_entry)

    if not match:
        msg = "The date was not found in the following log entry: {}".format(log_entry)
        raise DateNotFound(msg)

    timestamp_str = match.group().replace('[', '').replace(']', '').strip()
    timestamp = parser.parse(timestamp_str, fuzzy=True)

    return timestamp


def extract_url(log_entry):
    """Given a log entry, return a Python object representing the string."""
    pattern = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
    url = re.findall(pattern, log_entry)[0]

    if not url:
        raise URINotFound(log_entry)

    return urlparse(url)


def extract_deploy_id(log_entry):
    url = extract_url(log_entry)

    return url.netloc.split('.')[0].split('-')[-1]


class LogEntry(object):

    def __init__(self, log_string):
        self.timestamp = extract_timestamp(log_string)
        self.url = extract_url(log_string)
        self.deploy_id = extract_deploy_id(log_string)

    def __str__(self):
        "LogEntry(timestamp={}, url={}, deploy_id={})".format(self.timestamp,
                                                              self.url,
                                                              self.deploy_id
                                                              )


def entryparse(log_entry):

    return LogEntry(log_entry)
