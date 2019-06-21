#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Policy object class."""
from pacifica.policy.status.instrument.by_project_id import InstrumentsByProject
from pacifica.policy.status.instrument.search import InstrumentKeywordSearch


# pylint: disable=too-few-public-methods
class InstrumentQuery(object):
    """CherryPy root object class."""

    exposed = False

    def __init__(self):
        """Create local objects for sub tree items."""
        # self.search = ProjectSearch()
        self.by_project_id = InstrumentsByProject()
        self.search = InstrumentKeywordSearch()
