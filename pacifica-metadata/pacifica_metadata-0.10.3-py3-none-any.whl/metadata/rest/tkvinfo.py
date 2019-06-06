#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Transaciton Key Value Upload Base CherryPy."""
from pacifica.metadata.rest.tkvinfo_queries.values_for_key import ValuesForKey
from pacifica.metadata.rest.tkvinfo_queries.kvs_for_transaction import KVsForTransaction


# pylint: disable=too-few-public-methods
class TkvInfoAPI(object):
    """Transaction Key Value Info API."""

    exposed = True

    def __init__(self):
        """Create local objects for subtree items."""
        self.values_for_key = ValuesForKey()
        self.kv_for_transaction = KVsForTransaction()
