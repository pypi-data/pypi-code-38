#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Metadata Instrument Categories Class."""
from cherrypy import tools
from pacifica.metadata.orm import InstrumentGroup, Groups
from pacifica.metadata.rest.instrument_queries.query_base import QueryBase


class InstrumentCategories(QueryBase):
    """Calculates a set of instrument categories from the display names of EUS instruments."""

    exposed = True

    @staticmethod
    def get_instrument_categories():
        """Pull the full list of instrument categories from the DB."""
        # pylint: disable=no-member
        category_collection = (
            Groups
            .select(Groups, InstrumentGroup.instrument)
            .join(InstrumentGroup)
            .order_by(Groups.id)
        )
        # pylint: enable=no-member
        category_list = {}
        for cat in category_collection.dicts():
            if cat['id'] not in category_list:
                category_list[cat['id']] = {
                    'category': cat['name'],
                    'instrument_list': []
                }
            category_list[cat['id']]['instrument_list'].append(
                cat['instrument'])
        return list(category_list.values())

    # CherryPy requires these named methods
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    def GET():
        """CherryPy GET method."""
        return InstrumentCategories.get_instrument_categories()
