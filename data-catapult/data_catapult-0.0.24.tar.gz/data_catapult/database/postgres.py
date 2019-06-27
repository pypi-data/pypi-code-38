import tempfile
import re
from pandas.io.sql import SQLDatabase


class PostgresDriver(object):
    def __init__(self, engine):
        self.engine = engine

    def to_sql(self, df, schema_name, table_name, dtype=None):
        if dtype:
            for col, kind in dtype.items():
                if col not in df:
                    continue
                if kind in ["integer", "int", "bigint", "tinyint", "smallint", "hugeint"]:
                    df.loc[df[col].notnull(), col] = df.loc[df[col].notnull(), col].astype(int).astype(str)

        self._make_schema(df, schema_name, table_name, dtype)
        self._write_table(df, schema_name, table_name)

    def add_pk(self, schema_name, table_name, pk_cols):
        """Use pandas' functionality to automatically generate a schema"""
        pk_str = ",".join(pk_cols)
        create_pk_sql = 'ALTER TABLE {}."{}" ADD PRIMARY KEY ({});'.format(schema_name, table_name, pk_str)
        conn = self.engine.raw_connection()

        with conn.cursor() as cur:
            try:
                print(create_pk_sql)
                cur.execute(create_pk_sql)
                conn.commit()
            except Exception as err:
                print("[ERROR]", err)
            finally:
                conn.close()

    def _make_schema(self, dataframe, schema_name, table_name, dtype=None):
        """Use pandas' functionality to automatically generate a schema"""
        create_schema_sql = 'CREATE SCHEMA IF NOT EXISTS {};'.format(schema_name)
        sdb = SQLDatabase(self.engine, schema=schema_name)
        sql_str = sdb._create_sql_schema(dataframe, table_name)  # TODO: support keys param?
        if dtype:
            for col, db_type in dtype.items():
                pattern = r'("?{}"?)\s([A-Za-z0-9\\)\\(]+)'.format(col)
                new_db_type = r"\1 " + db_type
                sql_str = re.sub(pattern, new_db_type, sql_str)
        conn = self.engine.raw_connection()

        with conn.cursor() as cur:
            try:
                print(sql_str)
                cur.execute(create_schema_sql)
                cur.execute(sql_str)
                conn.commit()
            except Exception as err:
                print("[ERROR]", err)
            finally:
                conn.close()

    def _write_table(self, df, schema_name, table_name, encoding='utf-8'):
        """Write a given table to the Postgres databse. If the table does not already exist,
        it will be created."""
        cols = ['"{}"'.format(col) for col in df.columns]
        cols = ",".join(cols)
        conn = self.engine.raw_connection()

        with conn.cursor() as cur, tempfile.NamedTemporaryFile(mode='w+') as temp_file:
            df.to_csv(temp_file, index=False)
            temp_file.seek(0)
            print("Importing from", temp_file.name, "...")
            tmp_name = '"{}"."{}"'.format(schema_name, table_name)
            cmd = "COPY {} ({}) FROM STDIN WITH CSV HEADER DELIMITER ',';".format(tmp_name, cols)
            print(cmd)
            cur.copy_expert(cmd, temp_file)
            conn.commit()
        conn.close()
