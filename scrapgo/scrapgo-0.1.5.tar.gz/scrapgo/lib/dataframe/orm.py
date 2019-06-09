from collections import abc
import sqlite3

import pandas as pd
import pymysql
from sqlalchemy import create_engine

from scrapgo.utils.fileutils import get_file_extension, read_json, read_conf
from .dfutils import get_difference_from


QUERY_FORMAT = {
    'select': "SELECT {columns} FROM {table}",
    'select-where': "SELECT {columns} FROM {table} WHERE {where}",
    'max': "SELECT MAX({column}) FROM {table}",
    'max-where': "SELECT MAX({column}) FROM {table} WHERE {where}",
    'min': "SELECT MIN({column}) FROM {table}",
    'min-where': "SELECT MIN({column}) FROM {table} WHERE {where}",
    'count': "SELECT COUNT(*) FROM {table}",
    'count-where': "SELECT COUNT(*) FROM {table} WHERE {where}",
    'delete': "DELETE FROM {table}",
    'delete-where': "DELETE FROM {table} WHERE {where}",
}


def _join_columns(df, column, type=str):
    if type is str:
        clause = ','.join(f'"{k}"' for k in df[column].values)
    else:
        clause = ','.join(df[column].values)
    return clause  

class TableFrame(object):

    def __init__(self, db_conf_path=None, **conn_info):
        self.con = None
        if db_conf_path is not None:
            ext = get_file_extension(db_conf_path)
            if ext in ['.json']:
                conn_info = read_json(db_conf_path)
            elif ext in ['.cnf', '.conf']:
                conn_info = read_conf(db_conf_path, header='database')
            else:
                raise ValueError(
                    f"{ext} is not DB connection setting file extension(Only support .json, .cnf, .conf)"
                )  
        self.con = self._get_db_connection(**conn_info)

    def __del__(self):
        if self.con:
            self.con.close()

    def _get_db_connection(self, **kwargs):
        db_backend = kwargs.pop('backend', 'sqlite3')
        if db_backend == 'sqlite3': 
            con = sqlite3.connect(**kwargs)
        elif db_backend == 'mysql':
            con_str_fmt = "mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}?charset={charset}"
            con_str = con_str_fmt.format(**kwargs)
            engin = create_engine(con_str, encoding='utf-8')
            con = engin.connect()
        else:
            raise ValueError("DB backend only supported in sqlite3, mysql")
        return con
    
    def close(self):
        self.con.close()

    def _get_now(self):
        return pd.Timestamp.now()

    def _get_query(self, kind, table, query_formats=QUERY_FORMAT, **kwargs):
        fmt = query_formats[kind]
        return fmt.format(table=table, **kwargs)

    def get_dataframe(self, query, **kwargs):
        try:
            dataframe = pd.read_sql(query, self.con, **kwargs)
        except Exception as e:
            print(e)
        else:
            return dataframe

    def select(self, table, columns=None, where=None):
        if columns is None:
            columns = '*'
        else:
            columns = ','.join(columns)
        if where is None:
            query = self._get_query('select', table, columns=columns)
        else:
            query = self._get_query(
                'select-where', table, columns=columns, where=where
            )
        df = self.get_dataframe(query)
        return df

    def max(self, table, column, where=None, **kwargs):
        if where is None:
            query = self._get_query('max', table, column=column, **kwargs)
        else:
            query = self._get_query(
                'max-where', table,
                column=column, where=where, **kwargs
            )
        df = self.get_dataframe(query)
        if df is not None:
            return df.loc[0, f"MAX({column})"]

    def min(self, table, column, where=None, **kwargs):
        if where is None:
            query = self._get_query('min', table, column=column, **kwargs)
        else:
            query = self._get_query(
                'min-where', table,
                column=column, where=where, **kwargs
            )
        df = self.get_dataframe(query)
        if df is not None:
            return df.loc[0, f"MIN({column})"]

    def count(self, table, where=None, **kwargs):
        if where is None:
            query = self._get_query('count', table, **kwargs)
        else:
            query = self._get_query(
                'count-where', table, where=where, **kwargs
            )
        df = self.get_dataframe(query)
        if df is not None:
            return df.loc[0, "COUNT(*)"]
        return 0

    def insert(self, dataframe, table, uniques, renames=None, updated=None, created=None, if_exists='append', logging=True, **kwargs):
        if dataframe.empty is True:
            if logging is True:
                print(f"Dataframe is empty {0} ROW(s) was Inserted into {table} ({self._get_now()})")
            return

        if renames is not None:
            dataframe = dataframe.rename(columns=renames)
        
        if if_exists == 'append':
            df_table = self.select(table, uniques, **kwargs)
            if df_table is not None:
                dataframe = get_difference_from(dataframe, df_table, uniques)

        if dataframe.empty is False:            
            if updated is not None:
                dataframe[updated] = self._get_now()
            if created is not None:
                dataframe[created] = self._get_now()

            dataframe.to_sql(
                table, self.con,
                if_exists=if_exists,
                index=False
            )
        if logging is True:
            count = dataframe.shape[0]
            print(f"{count} ROW(s) was Inserted into {table} ({self._get_now()})")

    
    def update(self, dataframe, table, source_column, dest_column, valuemap=None, on=None, index=None, pk=None, default=None, value_type=str, pk_type=str, logging=True):
        if dataframe.empty is True:
            if logging is True:
                print(f"Dataframe is empty {0} ROW(s) was Updated to {table} ({self._get_now()})")
            return

        fmt = "UPDATE {table} SET {column}={value} WHERE {column} != {value} AND {pk} IN ({pk_values})"
        for value, df in dataframe.groupby(source_column):
            if isinstance(valuemap, abc.Mapping):
                value = valuemap.get(value, default or value)
            elif callable(valuemap):
                value = valuemap(value)
            else:
                value = default or value
            
            if value_type is str:
                value = f'"{value}"'
            pk_values = _join_columns(df, on or index, pk_type)
            query = fmt.format(
                table=table,
                column=dest_column,
                value=value,
                pk= on or pk,
                pk_values=pk_values,    
            )
            if logging is True:
                count = df.shape[0]
                print(f"{count} ROW(s) was Updated into {table} by Query: {query[:80]}... ({self._get_now()})")
            self.con.execute(query)
    
    def delete(self, table, where=None, logging=True):
        if where is None:
            count = self.count(table)
            query = self._get_query('delete', table=table)
        else:
            count = self.count(table, where=where)
            query = self._get_query(
                'delete-where', table=table, where=where
            )
        self.con.execute(query)
        if logging is True:
            print(f"{count} ROW(s) was Deleted by Query: {query}")



