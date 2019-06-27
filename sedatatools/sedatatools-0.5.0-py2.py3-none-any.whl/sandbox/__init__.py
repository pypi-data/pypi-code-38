import sqlalchemy as sa
import pyodbc
import pandas as pd


class Config:
    def __init__(self, usern, passw, connection_str, tc, server, db, system='win', sql_t='mssql'):
        self.username = usern
        self.password = passw
        self.connection_string = connection_str
        self.trusted_connection = tc
        self.server_name = server
        self.db_name = db
        self.system_type = system
        self.sql_type = sql_t
        # username = ''
        # password = ''
        # connection_string = ''
        # trusted_connection = False
        # server_name = ''
        # db_name = ''


localhost = Config(None, None, None, True, 'DS012\SQLEXPRESS', 'sandbox')
localhost_lin = Config(None, None, None, True, 'localhost', 'sandbox', 'win', 'postgres')
prime = Config('XXXXXXXXXX', 'xxxxx', None, False, 'prime', 'sandbox')


def load_data(t_name: str, configuration=localhost) -> pd.DataFrame():
    """
    This is the function to load the data from your sandbox.
    It uses your local db by default.
    """
    connection_string = create_connection_string(configuration)
    engine = sa.create_engine(connection_string)

    return pd.read_sql_table(table_name=t_name, con=engine)


def create_connection_string(configuration):
    if configuration.system_type == 'win':
        if configuration.sql_type == 'mssql':
            if configuration.trusted_connection:
                connection_string = f'mssql+pyodbc://{configuration.server_name}/{configuration.db_name}' \
                                    f'?driver=SQL+Server+Native+Client+11.0'
            else:
                connection_string = f'mssql+pyodbc://{configuration.username}:{configuration.password}@' \
                                    f'{configuration.server_name}/{configuration.db_name}'
        elif configuration.sql_type == 'postgres':
            connection_string = f'postgresql://{configuration.username}:{configuration.password}@{configuration.server_name}:5432/syncwrite'
    else:
        pass  # TODO check if there is a difference between platforms
    return connection_string


def load_data_merged(table_names, how=['inner'], merge_column='FIPS'):
    """
    This is used when you want to merge two tables but don't need to download
    them on your computer. This will do the merge on db server.
    """

    # TODO this is just an example, this needs to be created properly
    if len(table_names) - 1 != len(how) and len(table_names) > 2:
        print('Number of joins must be one less than number of tables!')
        return None
    sql_stat = 'SELECT * FROM ' + table_names[0] + ' ' + how[0] + ' join ' + table_names[1] + ' on ' + table_names[0] \
               + '.' + merge_column + ' = ' + table_names[1] + '.' + merge_column + ';'
    con = pyodbc.connect(
        r'DRIVER={ODBC Driver 11 for SQL Server};'
        r'SERVER=DS012\SQLEXPRESS;'
        r'DATABASE=sandbox;'
        r'Trusted_Connection=yes;'
    )
    return con.execute(sql_stat)


def load_data_filtered(table_name, condition, filter_column='FIPS'):
    """
    This is used if you want to download filtered table withou downloading the whole table to your computer.
    """
    sql_stat = 'SELECT * FROM ' + table_name + 'where ' + filter_column + ' like ' + condition + ';'
    con = pyodbc.connect(
        r'DRIVER={ODBC Driver 11 for SQL Server};'
        r'SERVER=DS012\SQLEXPRESS;'
        r'DATABASE=sandbox;'
        r'Trusted_Connection=yes;'
    )
    return con.execute(sql_stat)


def save_data(obj_to_save: pd.DataFrame(), t_name: str, configuration=localhost) -> None:
    """
    This is the main function to save the data to your sandbox.
    """
    if configuration.trusted_connection:
        engine = sa.create_engine(
            f'mssql+pyodbc://{configuration.server_name}/{configuration.db_name}?driver=SQL+Server+Native+Client+11.0')
    else:
        engine = sa.create_engine(
            f'mssql+pyodbc://{configuration.username}:{configuration.password}@{configuration.server_name}/'
            f'{configuration.db_name}?driver=SQL+Server+Native+Client+11.0')
    obj_to_save.to_sql(name=t_name, con=engine)
