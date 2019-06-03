from bamboo_lib.connectors.models import BaseDriver
from data_catapult.database.clickhouse import ClickhouseDriver as CatapultCd
from urllib.parse import urlparse


class ClickhouseDriver(BaseDriver):
    """
    Driver that allows bulk data exports to Postgres databases.

    Example usage:

    >>> import pandas as pd
    >>> df = pd.DataFrame({"id": ['a', 'b'], "val": [1, 2]})
    >>> chd = ClickhouseDriver(uri="clickhouse://user:pw@localhost/db_name")
    >>> chd_v2 = ClickhouseDriver(host="localhost", database="db_name", user="user", password="pw")
    >>> chd.write_df("my_new_table", df, pk=["id"])
    """
    TYPE = 'Clickhouse Bulk Write Driver'

    @staticmethod
    def parse_uri(uri):
        """ Checks a URI string that a user passes in and parses it into its components

        :param uri: URI string in format of clickhouse://user:pw@localhost/db_name
        :return: Dictionary with objects for connection settings
        """
        if not uri:
            return None
        result = urlparse(uri)
        host = result.hostname
        username = result.username if result.username else "default"
        password = result.password if result.password else ""

        port = result.port if result.port else 9000
        # use result.path[1:] to skip leading /
        database = result.path[1:] if result.path else "default"
        my_settings = {
            "host": host,
            "port": port,
            "database": database,
            "user": username,
            "password": password
        }
        return my_settings

    def __init__(self, **kwargs):
        super(ClickhouseDriver, self).__init__(**kwargs)
        uri_settings = ClickhouseDriver.parse_uri(kwargs.get("uri", None))
        if not uri_settings:
            self.settings = {
                "host": kwargs.get("host", "localhost"),
                "port": int(kwargs.get("port", 9000)),
                "database": kwargs.get("database", "default"),
                "user": kwargs.get("user", "default"),
                "password": kwargs.get("password", "")
            }
        else:
            self.settings = uri_settings

    def write_df(self, table_name, df, **kwargs):
        chd = CatapultCd(**self.settings)
        # TODO support for schema names and explicit dtypes
        # dtype = kwargs.get("dtype", None)
        return chd.to_sql(df, table_name, **kwargs)
