#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy File Details object class."""
from datetime import datetime
from dateutil.parser import parse
from cherrypy import tools
from pacifica.metadata.orm import TransactionKeyValue, Keys, Values, TransSIP
from pacifica.metadata.orm.base import db_connection_decorator
try:
    from urllib.parse import unquote
except ImportError:  # pragma: no cover
    from urlparse import unquote


# pylint: disable=too-few-public-methods
class ValuesForKey(object):
    """Retrieves a list of values for a given key from the trans_key_value table."""

    exposed = True

    @staticmethod
    def get_values_for_key(key, start_time, end_time):
        """Retrieve all the tkv values for a given key item."""
        # get the id of the key to look for
        val_list = (Values
                    .select(Values.value, TransactionKeyValue.transaction)
                    .join(TransactionKeyValue)
                    .join(Keys)
                    .join(TransSIP, on=(TransSIP.id == TransactionKeyValue.transaction))
                    .where(Keys.key == key)
                    .where(TransSIP.created < end_time)
                    .where(TransSIP.created >= start_time)).dicts()
        ret = {}
        for val in val_list:
            if val.get('value') not in ret:
                ret[val.get('value')] = []
            ret[val.get('value')].append(val.get('transaction'))
        return ret

    # Cherrypy requires these named methods.
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_out()
    @db_connection_decorator
    def GET(key, start_time=None, end_time=None):
        """Return file details for the given key/value combo."""
        key = unquote(key)
        if start_time:
            start_time = parse(start_time)
        else:
            start_time = datetime.utcfromtimestamp(0)
        if end_time:
            end_time = parse(end_time)
        else:
            end_time = datetime.utcnow()
        assert start_time < end_time
        return ValuesForKey.get_values_for_key(key, start_time, end_time)
