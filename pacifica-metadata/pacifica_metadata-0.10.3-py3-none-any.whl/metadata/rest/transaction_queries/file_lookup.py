#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status File Metadata object class."""
import re
import cherrypy
from cherrypy import tools, HTTPError
from pacifica.metadata.rest.transaction_queries.query_base import QueryBase
from pacifica.metadata.orm.base import db_connection_decorator


class FileLookup(QueryBase):
    """Retrieves file listing for an individual transaction."""

    exposed = True

    # Cherrypy requires these named methods.
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    @db_connection_decorator
    def GET(transaction_id=None):
        """Return File entries from the specified transaction entity."""
        if transaction_id is not None and re.match('[0-9]+', transaction_id):
            cherrypy.log.error('file details request')
            return QueryBase._get_file_list(transaction_id)
        else:
            message = 'Invalid file details lookup request. '
            message += "'{0}' is not a valid transaction_id".format(
                transaction_id)
            cherrypy.log.error(message)
            raise HTTPError(
                status='400 Invalid Request Options',
                message=QueryBase.compose_help_block_message()
            )
