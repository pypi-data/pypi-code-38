import sqlalchemy
from bamboo_lib.connectors.models import BaseDriver


class DatabaseDriver(BaseDriver):
    TYPE = 'SQL Alchemy Driver'

    def __init__(self, **kwargs):
        super(DatabaseDriver, self).__init__(**kwargs)
        self.engine = sqlalchemy.create_engine(self.uri)

    def write_df(self, table_name, df, **kwargs):
        return df.to_sql(table_name,
                         self.engine,
                         **kwargs)
