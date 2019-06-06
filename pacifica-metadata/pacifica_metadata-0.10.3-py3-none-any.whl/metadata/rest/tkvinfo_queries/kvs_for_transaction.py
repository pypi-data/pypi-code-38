#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy File Details object class."""
from cherrypy import tools
from pacifica.metadata.orm import TransactionKeyValue, Keys, Values
from pacifica.metadata.orm.base import db_connection_decorator


# pylint: disable=too-few-public-methods
class KVsForTransaction(object):
    """Retrieves a list of key/value pairs for a transaction_id."""

    exposed = True

    @staticmethod
    def get_kv_pairs_for_transaction(transaction_id):
        """Retrieve a list of key/value pairs for a transaction_id."""
        # pylint: disable=no-member
        tkv_query = (TransactionKeyValue
                     .select(Keys.key, Values.value)
                     .join(Keys,
                           on=(TransactionKeyValue.key == Keys.id))
                     .join(Values,
                           on=(TransactionKeyValue.value == Values.id))
                     .where(TransactionKeyValue.transaction == transaction_id)).dicts()
        # pylint: enable=no-member
        return {str(item['key']): str(item['value']) for item in tkv_query}

    # Cherrypy requires these named methods.
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    @db_connection_decorator
    def GET(transaction_id):
        """Return key/value combos for a given transaction."""
        return KVsForTransaction.get_kv_pairs_for_transaction(transaction_id)
