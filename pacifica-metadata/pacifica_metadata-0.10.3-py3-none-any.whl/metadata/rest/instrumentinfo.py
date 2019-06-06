#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Core interface for the projectinfo metadata objects to interface with CherryPy."""
from pacifica.metadata.rest.instrument_queries.instrument_lookup import InstrumentLookup
from pacifica.metadata.rest.instrument_queries.instrument_term_search import InstrumentTermSearch
from pacifica.metadata.rest.instrument_queries.instrument_user_search import InstrumentUserSearch
from pacifica.metadata.rest.instrument_queries.instrument_categories import InstrumentCategories


# pylint: disable=too-few-public-methods
class InstrumentInfoAPI(object):
    """InstrumentInfo API."""

    exposed = True

    def __init__(self):
        """Create local objects for subtree items."""
        self.search = InstrumentTermSearch()
        self.by_instrument_id = InstrumentLookup()
        self.by_user_id = InstrumentUserSearch()
        self.categories = InstrumentCategories()
