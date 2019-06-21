"""Module for importing data into MonetDB databases"""
import tempfile
from pandas.io.sql import get_schema
# monetdb.sql
TYPE = 'type'


class MonetDBDriver(object):
    def __init__(self, conn):
        self.conn = conn

    def to_sql(self, df, schema_name, table_name, dtype=None, overwrite=False, table_schema_only=False, data_only=False):
        if dtype:
            for col, kind in dtype.items():
                if col not in df:
                    continue
                if kind in ["integer", "int", "bigint", "tinyint", "smallint", "hugeint"]:
                    df.loc[df[col].notnull(), col] = df.loc[df[col].notnull(), col].astype(int).astype(str)

        if not data_only:
            self._make_schema(df, schema_name, table_name, dtype, overwrite)
        if not table_schema_only:
            self._write_table(df, schema_name, table_name)

    def _make_schema(self, df, schema_name, table_name, dtype=None, overwrite=False):
        """Use pandas' functionality to automatically generate a schema"""
        conn = self.conn
        cur = conn.cursor()
        tmp_name = "CREATE TABLE {}.{}".format(schema_name, table_name)
        sql_str = get_schema(df, table_name, dtype=dtype)
        sql_str = sql_str.replace(r'CREATE TABLE "{}"'.format(table_name), tmp_name)
        print(sql_str)
        create_schema_sql = 'CREATE SCHEMA {};'.format(schema_name)
        try:
            cur.execute(create_schema_sql)
            conn.commit()
        except:
            conn.rollback()
            print("[WARNING] Schema exists...")
        if overwrite:
            try:
                cur.execute("Drop table {}".format(tmp_name))
                conn.commit()
            except Exception as err:
                print("[WARNING] Dropping table that does not exist...", err)
                conn.rollback()
        try:
            cur.execute(sql_str)
            conn.commit()
        except Exception as err:
            print("[WARNING] Table already exists...", err)
            conn.rollback()

    def lookup_columns(self, cursor, schema, table):
        table = table.lower()
        query = """
            SELECT name as column_name FROM sys.columns
            WHERE table_id=(SELECT id FROM sys.tables WHERE name='{}'
            AND schema_id=(select id FROM sys.schemas where name = '{}'));
        """.format(table, schema)
        print(query)
        cursor.execute(query)
        res = cursor.fetchall()
        cols_in_order = [x[0] for x in res]
        return cols_in_order

    def _write_table(self, df, schema_name, table_name):
        """Write a given table to the Postgres databse. If the table does not already exist,
        it will be created."""
        conn = self.conn

        with tempfile.NamedTemporaryFile(mode='w+') as temp_file:
            cur = conn.cursor()
            table_cols = self.lookup_columns(cur, schema_name, table_name)
            df.to_csv(temp_file, index=False)
            temp_file.seek(0)
            cols = [u'"{}"'.format(col) for col in df.columns]
            cols = u"({})".format(u",".join(cols))
            print("Importing from", temp_file, "...", dir(cur))
            # print dir()
            tmp_name = "{}.{}".format(schema_name, table_name)
            cur.copy_from(temp_file, tmp_name, string_quote=u'"', null_string=u'', field_separator=u',', offset=2, cols=list(df.columns), table_col_order=table_cols)
            conn.commit()

    def add_pk(self, full_table_name, pk, database_settings=None):
        if not isinstance(pk, list):
            raise ValueError("Primary key must be provided in list format")
        conn = self.conn
        pk = ['"{}"'.format(col_name) for col_name in pk]
        pk_str = ','.join(pk)
        pk_id = full_table_name.replace(".", "_")
        sql_str = 'ALTER TABLE {} ADD CONSTRAINT pk_{}_id PRIMARY KEY ({});'.format(full_table_name, pk_id, pk_str)
        cur = conn.cursor()
        print('EXECUTING:', sql_str)
        try:
            cur.execute(sql_str)
            conn.commit()
        except:
            print('Could not add Primary Key.')
