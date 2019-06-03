from bamboo_lib.connectors.models import BaseDriver
from data_catapult.database.monetdb import MonetDBDriver as CatapultMdb
import monetdb.sql
from sqlalchemy.engine.url import make_url


class MonetDriver(BaseDriver):
    TYPE = 'MonetDB Bulk Write Driver'

    def __init__(self, **kwargs):
        super(MonetDriver, self).__init__(**kwargs)

        username = kwargs.get("username", "monetdb")
        password = kwargs.get("password", "monetdb")
        hostname = kwargs.get("hostname", "localhost")
        database = kwargs.get("database", "public")
        # port = int(kwargs.get("port", 50000)) # TODO accept port

        if kwargs.get("uri", None):
            db_uri = make_url(kwargs["uri"])
            username = db_uri.username
            hostname = db_uri.host
            password = db_uri.password
            database = db_uri.database

        self.conn = monetdb.sql.connect(username=username,
                                        password=password,
                                        hostname=hostname,
                                        database=database)

    def write_df(self, table_name, df, **kwargs):
        mdb = CatapultMdb(self.conn)
        schema_name = kwargs.get("schema", "public")
        dtype = kwargs.get("dtype", None)
        table_schema_only = kwargs.get("table_schema_only", None)
        data_only = kwargs.get("data_only", None)
        return mdb.to_sql(df, schema_name, table_name, dtype, table_schema_only=table_schema_only, data_only=data_only)

    def add_pk(self, *args):
        mdb = CatapultMdb(self.conn)
        return mdb.add_pk(*args)
