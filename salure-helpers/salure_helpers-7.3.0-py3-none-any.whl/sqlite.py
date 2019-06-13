import json
import sqlite3
import time
import pandas as pd


class SQLite:

    def __init__(self, database_location):
        self.connection = sqlite3.connect(database_location)


    def create_table(self, table, dataframe):
        start = time.time()
        # Map dataframe datatypes to monetdb datatypes. First in set is dataframe type, second is monetdb.
        datatypes =[
            {'dataframe_type': 'int64', 'sqlite_type': 'INTEGER'},
            {'dataframe_type': 'object', 'sqlite_type': 'TEXT'},
            {'dataframe_type': 'float64', 'sqlite_type': 'REAL'},
            {'dataframe_type': 'datetime64[ns]', 'sqlite_type': 'TEXT'},
            {'dataframe_type': 'bool', 'sqlite_type': 'TEXT'}
        ]
        datatypes = pd.DataFrame(datatypes)

        # Create a dataframe with all the types of the given dataframe
        dataframe_types = pd.DataFrame({'columns': dataframe.dtypes.index, 'types': dataframe.dtypes.values})
        dataframe_types = dataframe_types.to_json()
        dataframe_types = json.loads(dataframe_types)
        dataframe_types_columns = []
        dataframe_types_types = []

        for field in dataframe_types['columns']:
            dataframe_types_columns.append(dataframe_types['columns'][field])

        for type in dataframe_types['types']:
            dataframe_types_types.append(dataframe_types['types'][type]['name'])

        dataframe_types = pd.DataFrame({'columns': dataframe_types_columns, 'dataframe_type': dataframe_types_types})
        columns = pd.merge(dataframe_types, datatypes, on='dataframe_type', how='left')
        headers = ''
        for index, row in columns.iterrows():
            value = row['columns'] + ' ' + row['sqlite_type']
            headers += ''.join(value) + ', '
        headers = headers[:-2]

        try:
            cursor = self.connection.cursor()
            cursor.execute('CREATE TABLE IF NOT EXISTS {0} ({1})'.format(table, headers))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e

        print('{0} End - Created table {1} in {2} seconds'.format(time.strftime('%H:%M:%S'), table, time.time() - start))


    def drop_table(self, table):
        cursor = self.connection.cursor()

        cursor.execute('DROP TABLE {0}'.format(table))
        self.connection.commit()
        self.connection.close()


    def insert(self, table, dataframe):
        start = time.time()

        cursor = self.connection.cursor()

        tableHeaders = ', '.join(list(dataframe))
        dataframe = dataframe.reset_index(drop=True)
        values = ','.join(str(index[1:]) for index in dataframe.itertuples())
        query = 'INSERT INTO {0} ({1}) VALUES {2}'.format(table, tableHeaders, values)
        print(query)
        cursor.execute(query)

        end = time.time()
        print('{0} Inserting data took {1}'.format(time.strftime('%H:%M:%S'), end - start))

        self.connection.commit()


    def replace(self, table, dataframe):
        start = time.time()

        cursor = self.connection.cursor()

        tableHeaders = ', '.join(list(dataframe))
        dataframe = dataframe.reset_index(drop=True)
        values = ','.join(str(index[1:]) for index in dataframe.itertuples())

        query = 'REPLACE INTO {0} ({1}) VALUES {2}'.format(table, tableHeaders, values)
        cursor.execute(query)

        end = time.time()
        print('{0} Replacing data took {1}'.format(time.strftime('%H:%M:%S'), end - start))

        self.connection.commit()


    def delete(self, table, filter=''):
        start = time.time()

        cursor = self.connection.cursor()

        cursor.execute('DELETE FROM {0} {1}'.format(table, filter))

        self.connection.commit()
        self.connection.close()

        print('%s End - Deleting data from %s took %f seconds' % (time.strftime('%H:%M:%S'), table, time.time() - start))


    def select(self, table, selection, filter=''):
        start = time.time()
        # print('%s Start - Selecting data from %s' % (time.strftime('%H:%M:%S'), table))

        cursor = self.connection.cursor()
        cursor.execute('SELECT {0} FROM {1} {2}'.format(selection, table, filter))
        data = cursor.fetchall()
        self.connection.close()

        return data


    def close_connection(self):
        self.connection.close()