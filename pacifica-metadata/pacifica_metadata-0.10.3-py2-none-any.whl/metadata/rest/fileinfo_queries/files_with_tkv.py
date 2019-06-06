#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy File Details object class."""
from cherrypy import tools
from peewee import DoesNotExist, fn
from pacifica.metadata.orm import Files, TransactionKeyValue, Keys, Values
from pacifica.metadata.orm.base import db_connection_decorator
try:
    from urllib.parse import unquote
except ImportError:  # pragma: no cover
    from urlparse import unquote


# pylint: disable=too-few-public-methods
class FilesWithTransactionKeyValue(object):
    """Retrieves file details for a list of files having a certain key/value combo."""

    exposed = True

    @staticmethod
    def _get_files_for_kv_pair(key, value):
        # get the id of the key to look for
        try:
            k = Keys().select(Keys.id).where(fn.Lower(Keys.key) == key.lower()).get()
            val = Values().select(Values.id).where(Values.value == value).get()
            # pylint: disable=protected-access
            tkv_where_clause = TransactionKeyValue().where_clause(
                {'key_id': k.__data__['id'], 'value_id': val.__data__['id']})
            # pylint: enable=protected-access
            tkv_list = TransactionKeyValue().select().where(tkv_where_clause)
            transaction_list = [t.transaction_id for t in tkv_list]
            files_query = Files().select().where(Files.transaction << transaction_list)
        except DoesNotExist:
            # invalid value
            return []

        return [f.to_hash() for f in files_query]

    # Cherrypy requires these named methods.
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    @db_connection_decorator
    def GET(key, value):
        """Return file details for the given key/value combo."""
        key = unquote(key)
        value = unquote(value)
        return FilesWithTransactionKeyValue._get_files_for_kv_pair(key, value)
