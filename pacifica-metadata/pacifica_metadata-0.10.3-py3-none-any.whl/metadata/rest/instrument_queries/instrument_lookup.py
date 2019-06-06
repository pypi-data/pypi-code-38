#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Metadata object class."""
import re
import cherrypy
from cherrypy import tools, HTTPError
from peewee import DoesNotExist
from pacifica.metadata.orm import Instruments
from pacifica.metadata.rest.instrument_queries.query_base import QueryBase


# pylint: disable=too-few-public-methods
class InstrumentLookup(QueryBase):
    """Retrieves a set of projects for a given keyword set."""

    exposed = True

    @staticmethod
    def _get_instrument_details(instrument_id):
        """Return a formatted dictionary containing the details of a given Instrument entry."""
        terms = re.findall(r'[^+ ,;]+', str(instrument_id))
        for term in terms:
            # Take the first thing that matches standard project id numbering
            if re.match('[0-9]+', term):
                instrument_id = term
                break
        try:
            i = Instruments.select(
                Instruments.id, Instruments.display_name,
                Instruments.name, Instruments.name_short,
                Instruments.active
            ).where(Instruments.id == instrument_id).get()

        except DoesNotExist:
            message = 'No Instrument with an ID of {0} was found'.format(
                instrument_id)
            raise HTTPError('404 Not Found', message)

        return QueryBase.format_instrument_block(i)

    # CherryPy requires these named methods
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    def GET(instrument_id=None):
        """CherryPy GET method."""
        if instrument_id is not None and re.match('[0-9]+', instrument_id):
            cherrypy.log.error('instrument details request')
            return InstrumentLookup._get_instrument_details(instrument_id)
        else:
            message = 'Invalid instrument details lookup request. '
            message += "'{0}' is not a valid instrument_id".format(
                instrument_id)
            cherrypy.log.error(message)
            raise HTTPError(
                status='400 Invalid Request Options',
                message=QueryBase.instrument_help_block_message()
            )
