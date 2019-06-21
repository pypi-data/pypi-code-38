#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The CherryPy rest object for the structure."""
from pacifica.policy.reporting.transaction.transaction_summary import TransactionSummary
from pacifica.policy.reporting.transaction.transaction_details import TransactionDetails


# pylint: disable=too-few-public-methods
class ReportingPolicy(object):
    """
    CherryPy root object class.

    not exposed by default the base objects are exposed.

    """

    exposed = False

    def __init__(self):
        """Create local objects to allow for import to work."""
        self.transaction_summary = TransactionSummary()
        self.transaction_details = TransactionDetails()
# pylint: enable=too-few-public-methods
