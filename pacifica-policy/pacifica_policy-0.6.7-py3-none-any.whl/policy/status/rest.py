#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The CherryPy rest object for the structure."""
# from pacifica.policy.uploader.instrument import InstrumentQuery
from pacifica.policy.status.project_query import ProjectQuery
from pacifica.policy.status.instrument_query import InstrumentQuery
from pacifica.policy.status.transaction_query import TransactionQuery
from pacifica.policy.status.user_query import UserQuery


# pylint: disable=too-few-public-methods
class StatusPolicy(object):
    """
    CherryPy root object class.

    not exposed by default the base objects are exposed.

    """

    exposed = False

    def __init__(self):
        """Create local objects to allow for import to work."""
        self.instruments = InstrumentQuery()
        self.instrument = InstrumentQuery()
        self.projects = ProjectQuery()
        self.transactions = TransactionQuery()
        self.users = UserQuery()
# pylint: enable=too-few-public-methods
