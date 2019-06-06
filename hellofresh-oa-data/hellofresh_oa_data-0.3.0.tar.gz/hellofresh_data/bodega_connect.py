"""
    BodegaConnect is part of the hellofresh_data module
    meant for returning a bodega connection object for
    DB quering purposes. Note, if no variables are passed
    into the object a default, read only, user connection is returned.
"""
import os
import psycopg2
import yaml
from hellofresh_data import parameter_store

HOST_PATH = '/Prod/BodegaDB/host'
USER_PATH = '/Prod/BodegaDB/ro_user'
PASSWORD_PATH = '/Prod/BodegaDB/ro_password'

class BodegaConnect(object):
    """
        Base class for BodegaConnection
    """
    def __init__(self, bodega_user=None, bodega_password=None):

        self._conn = None
        self._bodega_user = None
        self._bodega_password = None

        self._bodega_host = \
        parameter_store.get_parameter_store_value(HOST_PATH)

        self.set_connection_credentials(bodega_user, bodega_password)


    def set_connection_credentials(self, bodega_user, bodega_password):
        """
            If no variables are passed into the object a default, read only,
            user connection is returned.
        """
        if bodega_user is None and bodega_password is  None:
            self._bodega_user = \
            parameter_store.get_parameter_store_value(USER_PATH)

            self._bodega_password = \
            parameter_store.get_parameter_store_value(PASSWORD_PATH)
        else:
            self._bodega_user = bodega_user
            self._bodega_password = bodega_password

    def bodega_connect(self):
        """
            Connecting to Bodega
        """
        try:
            self._conn = psycopg2.connect(
                dbname='US_Datamart',
                user=self._bodega_user,
                password=self._bodega_password,
                host=self._bodega_host,
                port=5432,
                sslmode='require'
                )
        except psycopg2.OperationalError as err:
            self._conn = None
            self._logger.error(err)

        return self._conn
