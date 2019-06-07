'''
Module containing easy_db DataBase class.
'''
import sqlite3
import pyodbc
import os
import time
from functools import lru_cache
from functools import wraps
import tqdm
import easy_multip
from . import util




class DataBase():

    def __init__(self, db_location_str: str='') -> None:
        self.db_location_str = db_location_str

        self.db_type = self._find_db_type()
        if self.db_type == 'ACCESS':
            self.connection = self._connection_access
        elif self.db_type == 'SQL SERVER':
            self.connection = self._connection_sql_server
        elif self.db_type == 'SQLITE3':
            self.connection = self._connection_sqlite



    def _find_db_type(self):
        '''
        Figure out what kind of databse is being used.
        '''
        if '.accdb' in self.db_location_str.lower() or '.mdb' in self.db_location_str.lower():
            return 'ACCESS'
        elif 'dsn' in self.db_location_str.lower():
            return 'SQL SERVER'
        elif util.check_if_file_is_sqlite(self.db_location_str):
            return 'SQLITE3'
        else:
            return 'Database not recognized!'


    def _connection_sqlite(self, also_cursor: bool=False, create_if_none: bool=False):
        '''
        Return a connection object to the Sqlite3 Database.
        '''
        db_file_exists = True if os.path.isfile(self.db_location_str) else False
        if db_file_exists or create_if_none:
            conn = sqlite3.connect(self.db_location_str)
            if also_cursor:
                return conn, conn.cursor()
            else:
                return conn
        else:
            print(f'The file {self.db_location_str} does not exist.')
            print('Please first create this database or specify create_if_none=True.')


    def _connection_access(self, also_cursor: bool=False):
        '''
        Return a connection object to the Access Database.
        '''
        conn = pyodbc.connect(
        r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};" +
        r'Dbq=' + self.db_location_str + ';')
        if also_cursor:
            return conn, conn.cursor()
        else:
            return conn


    def _connection_sql_server(self, also_cursor: bool=False):
        '''
        Return a connection object to the SQL Server Database.
        '''
        conn = pyodbc.connect(self.db_location_str)
        if also_cursor:
            return conn, conn.cursor()
        else:
            return conn


    def provide_db_connection(self, also_cursor=False):
        '''
        DECORATOR provides db connection (and cursor if requested) for database as first arg(s).
        Used to decorate functions that would like to manipulate conn and/or cursor directly.

        Connection commit and closing is handled at the end of this decorator method!
        '''
        def decorator(func):  # need extra layer of scope to handle the also_cursor kwarg passed in user code...
            @wraps(func)  # allows for decorated function's doctstring to come through decorator
            def inner(*args, **kwargs):
                conn = None
                counter = 0
                while conn is None:
                    try:
                        if also_cursor:
                            conn, cursor = self.connection(also_cursor=True)
                            cursor.arraysize = 50  # attempt to speed up cursor.fetchall() calls... not sure of impact
                        else:
                            conn = self.connection()
                    except (pyodbc.Error, sqlite3.OperationalError) as error:  # in case database is locked from another connection
                        time.sleep(0.01)
                        counter += 1
                        if counter > 1000:
                            print(f'ERROR!  Could not access {self.db_location_str}')
                            print('Database is locked from another connection!')
                            break

                returned = func(conn, cursor, *args, **kwargs) if also_cursor else func(conn, *args, **kwargs)

                try:
                    conn.commit()
                except:  # if database is locked
                    time.sleep(0.1)
                    conn.commit()
                finally:
                    conn.close()
                return returned
            return inner
        return decorator


    @lru_cache(maxsize=4)
    def pull_full_table(self, tablename: str) -> list:
        '''
        SELECT * Query for full table as specified from tablename.
        Return list of dicts for rows with column names as keys.
        '''
        sql = f'SELECT * FROM {tablename};'
        conn, cursor = self.connection(also_cursor=True)
        data = util.list_of_dicts_from_query(cursor, sql, tablename, self.db_type)
        conn.close()
        return data


    def pull_table_where(self, tablename: str, condition: str) -> list:
        '''
        SELECT * WHERE Query for table as specified from tablename and condition
        Return list of dicts for rows with column names as keys.
        '''
        sql = f'SELECT * FROM {tablename} WHERE {condition};'
        conn, cursor = self.connection(also_cursor=True)
        data = util.list_of_dicts_from_query(cursor, sql, tablename, self.db_type)
        conn.close()
        return data


    def pull_table_where_id_in_list(self, tablename: str, id_col: str, match_values: list, use_multip: bool=True) -> list:
        '''
        Pulls all data from table where id_col value is in the provided match_values_to_use.
        Can use multiprocessing if use_multip specifed as True.
        '''
        # if use_multip and len(match_values) >= 100:
            # return _pull_table_using_id_list_multip(match_values, *self.connection(also_cursor=True), tablename, id_col, self.db_type)
        # else:
            # if len(match_values) < 100:
                # print('Less than 100 match_values given to pull_table_using_id_list.  Using single process.')
            # return _pull_table_using_id_list(match_values, *self.connection(also_cursor=True), tablename, id_col, self.db_type)
        if use_multip:
            print('use_multip not yet working in pull_table_where_id_in_list().  Using single process.')
        return _pull_table_using_id_list(match_values, *self.connection(also_cursor=True), tablename, id_col, self.db_type)


    def pull_all_table_names(self) -> list:
        '''
        Return sorted list of all tables in the database.
        '''
        conn, cursor = self.connection(also_cursor=True)
        if self.db_type == 'SQLITE3':
            tables = [tup[0] for tup in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
        else:
            tables = cursor.tables()

        return sorted(tables)


    def table_columns_and_types(self, tablename: str) -> dict:
        '''
        Return dict of all column: type pairs in specified table.
        '''
        sql = f'SELECT * FROM {tablename} LIMIT 2;'
        conn, cursor = self.connection(also_cursor=True)
        data = util.list_of_dicts_from_query(cursor, sql, tablename, self.db_type)
        conn.close()
        if len(data) == 0:
            print(f'No rows in {tablename}.  Please determine columns and types with another method.')
            return None
        else:
            columns_and_types = {key: type(value).__name__ for key, value in data[0]}
            return columns_and_types


    def create_table(self, tablename: str, columns_and_types: dict, force_overwrite: bool=False):
        '''
        Create a table in the database with name "tablename"

        Pass in a dictionary containing column names as keys and column types as values.
        values can be tye actual type (like int, float, etc.) or strings of those same (like 'int', 'float', etc.)

        force_overwrite kwarg allows to overwrite existing table if present
        (by default will NOT overwrite/change existing table.)
        '''
        if tablename in self.pull_all_table_names() and not force_overwrite:
            print(f'ERROR!  Cannot create table {tablename} as it already exists!')
            print('Please choose a different name or use force_overwrite=True to overwrite.')

        conn, cursor = self.connection(also_cursor=True)

        if self.db_type == 'ACCESS':
            type_map = {float: 'double',
                        'float': 'double',
                        'double': 'double',
                        'float64': 'double',
                        'numpy.float64': 'double',
                        int: 'integer',
                        'int': 'integer',
                        'integer': 'integer',
                        str: 'CHAR',
                        'str': 'CHAR',
                        'text': 'CHAR',
                        }
            column_types = ', '.join([f'{k} {type_map[v]}' for k, v in columns_and_types])
            sql = f"CREATE TABLE {tablename}({column_types});"
        elif self.db_type == 'SQLITE3':
            type_map = {float: 'REAL',
                        'float': 'REAL',
                        'double': 'REAL',
                        'real': 'REAL',
                        'float64': 'REAL',
                        'numpy.float64': 'REAL',
                        int: 'INTEGER',
                        'int': 'INTEGER',
                        'integer': 'INTEGER',
                        str: 'TEXT',
                        'str': 'TEXT',
                        'text': 'TEXT',
                        }
            column_types = ', '.join([f'{k} {type_map[v]}' for k, v in columns_and_types.items()])
            sql = f"CREATE TABLE {tablename}({column_types});"
        else:
            print('ERROR!  Table creation only implemented in SQLite and Access currently.')
            return


        cursor.execute(sql)
        conn.commit()
        conn.close()
        print(f'Table {tablename} successfully created!')


    def append_to_table(self, tablename: str, data: list, create_table_if_needed: bool=True):
        '''
        Append rows of data to database table.
        Create the table in the database if it doesn't exist if create_table_if_needed is True

        "data" arg is list of row dicts where each row dict contains all columns as keys.
        '''
        if tablename not in self.pull_all_table_names():
            if create_table_if_needed:
                columns_and_types = {key: type(value).__name__ for key, value in data[0].items()}
                self.create_table(tablename, columns_and_types)
                columns = [col for col in columns_and_types]
            else:
                print(f'ERROR!  Table {tablename} does not exist in database!')
                print('Use create_table_if_needed=True if you would like to create it.')
                return None
        else:
            columns = [col for col in self.table_columns_and_types(tablename)]

        sql = f"INSERT INTO {tablename} ({', '.join([k for k in columns])}) VALUES ({', '.join(['?' for _ in range(len(columns))])});"
        data_to_insert = [tuple(row_dict[col] for col in columns) for row_dict in data]
        conn, cursor = self.connection(also_cursor=True)
        cursor.executemany(sql, data_to_insert)
        conn.commit()
        conn.close()
        print(f'Data inserted in {tablename}.  ({"{:,.0f}".format(len(data))} rows)')


    def __repr__(self) -> str:
        return f'DataBase: {self.db_location_str}'



def _pull_table_using_id_list(match_values_to_use: list, conn, cursor, tablename: str, id_col: str, db_type: str) -> list:
    '''
    Pulls all data from table where id_col value is in the provided match_values_to_use.
    Separate function here so easy_multip can be used if desired.
    '''
    @lru_cache(maxsize=4)
    def sql_str(subset_len: int) -> str:
        return f"SELECT * FROM {tablename} WHERE {id_col} in ({'?,'.join(['' for _ in range(subset_len)])}?);"

    data: list = []
    pbar = tqdm.tqdm(total=len(match_values_to_use))
    while len(match_values_to_use) > 0:
        subset = match_values_to_use[:25]
        sql = sql_str(len(subset))
        data.extend(util.list_of_dicts_from_query(cursor, sql, tablename, db_type, subset))
        match_values_to_use = match_values_to_use[25:]
        pbar.update(25)
    pbar.update(len(match_values_to_use) % 25)
    conn.close()
    return data
# _pull_table_using_id_list_multip = easy_multip.decorators.use_multip(_pull_table_using_id_list)  # decorate with multiprocessing
