#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy Status Transaction Metadata object class."""
from cherrypy import tools
from peewee import fn
from pacifica.metadata.rest.transaction_queries.query_base import QueryBase
from pacifica.metadata.orm import TransSIP
from pacifica.metadata.orm.base import db_connection_decorator


# pylint: disable=too-few-public-methods
class TransactionLast(QueryBase):
    """Retrieves details for an individual transaction."""

    exposed = True

    @staticmethod
    def _get_last_known_transaction():
        txn_id = (TransSIP
                  .select(fn.Max(TransSIP.id).alias('id'))
                  .where(TransSIP.deleted >> None)
                  .dicts()
                  .get())
        return {'latest_transaction_id': txn_id['id']}

    # Cherrypy requires these named methods.
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    @db_connection_decorator
    def GET():
        """Return details about the specified transaction entity."""
        return TransactionLast._get_last_known_transaction()
