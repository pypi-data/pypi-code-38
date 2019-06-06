#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Metadata object class."""
import re
import cherrypy
from cherrypy import tools
from peewee import OP, Expression, fn
from pacifica.metadata.orm import Instruments
from pacifica.metadata.rest.instrument_queries.query_base import QueryBase


class InstrumentTermSearch(QueryBase):
    """InstrumentTermSearch API."""

    exposed = True

    @staticmethod
    def search_for_instrument(search_term):
        """Return a dictionary containing information about a given instrument."""
        terms = re.findall(r'[^+ ,;]+', search_term)
        if not terms:
            return []
        keys = ['display_name', 'name_short', 'name', 'id']
        where_clause = Expression(1, OP.EQ, 1)
        for item in terms:
            term = str(item)
            where_clause_part = Expression(1, OP.EQ, 0)
            for k in keys:
                field = getattr(Instruments, k)
                if k == 'id':
                    if re.match('[0-9]+', term):
                        where_clause_part |= (
                            field == int(term)
                        )
                        where_clause_part |= (
                            fn.TO_CHAR(field, '99999999999').contains(term)
                        )
                else:
                    where_clause_part |= (
                        field.contains(term))
            where_clause &= (where_clause_part)

        objs = Instruments.select().where(where_clause).order_by(Instruments.name_short)
        if not objs:
            message = 'No instrument entries were retrieved using the terms: \''
            message += '\' and \''.join(terms) + '\''
            raise cherrypy.HTTPError(
                '404 No Valid Instruments Located', message)

        return [QueryBase.format_instrument_block(obj) for obj in objs]

    # pylint: disable=invalid-name
    # pylint: disable=duplicate-code
    @staticmethod
    @tools.json_out()
    def GET(search_term=''):
        """Return a set of instruments for a given user."""
        return InstrumentTermSearch.search_for_instrument(search_term)
