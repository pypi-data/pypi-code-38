#!/usr/bin/python3
import time
import sys
import psycopg2


class PostgreSql:

    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database


    def raw_query(self, query):
        try:
            connection = psycopg2.connect(host=self.host, port=5432, dbname=self.database, user=self.user, password=self.password)
            connection.autocommit = True
            cursor = connection.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
            connection.close()
            return data
        except Exception as e:
            return e


    def select_metadata(self, table):
        try:
            connection = psycopg2.connect(host=self.host, port=5432, dbname=self.database, user=self.user, password=self.password)
            cursor = connection.cursor()
            cursor.arraysize = 1
            cursor.execute('SELECT * FROM {0}'.format(table))
            metadata = cursor.description
            connection.close()

            columns = []
            for name in metadata:
                columns.append(name[0])

            return columns
        except Exception as e:
            return e


    def select(self, table, selection, filter=''):
        try:
            connection = psycopg2.connect(host=self.host, port=5432, dbname=self.database, user=self.user, password=self.password)
            cursor = connection.cursor()
            cursor.execute('SELECT {0} FROM {1} {2}'.format(selection, table, filter))
            data = cursor.fetchall()
            connection.close()
            return data
        except Exception as e:
            return e


    def insert(self, table, dataframe):
        try:
            start = time.time()
            connection = psycopg2.connect(host=self.host, port=5432, dbname=self.database, user=self.user, password=self.password)
            cursor = connection.cursor()
            tableHeaders = ', '.join(list(dataframe))
            dataframe = dataframe.reset_index(drop=True)
            values = ','.join(str(index[1:]) for index in dataframe.itertuples())
            values = values.replace('None', 'DEFAULT')
            datasize = sys.getsizeof(values)
            query = 'INSERT INTO {0} ({1}) VALUES {2}'.format(table, tableHeaders, values)
            cursor.execute(query)
            connection.commit()
            connection.close()
            return '{0} - Writing data ({1} bytes) took {2} seconds'.format(time.strftime('%H:%M:%S'), datasize, time.time() - start)
        except Exception as e:
            return e


    def copy_into(self, table, path_to_csv, field_separator=','):
        try:
            start = time.time()
            connection = psycopg2.connect(host=self.host, port=5432, dbname=self.database, user=self.user, password=self.password)
            cursor = connection.cursor()
            with open(path_to_csv, 'r') as file:
                # next(file)
                cursor.copy_from(file, table, sep=field_separator)
            connection.commit()
            connection.close()
            return '{} End - Writing data into {} took {} seconds'.format(time.strftime('%H:%M:%S'), table, time.time() - start)

        except Exception as e:
            return e


    def delete(self, table, filter=''):
        try:
            start = time.time()
            connection = psycopg2.connect(host=self.host, port=5432, dbname=self.database, user=self.user, password=self.password)
            cursor = connection.cursor()
            cursor.execute('DELETE FROM {0} {1}'.format(table, filter))
            connection.commit()
            connection.close()
            return '{0} - Deleting data took {1} seconds'.format(time.strftime('%H:%M:%S'), time.time() - start)
        except Exception as e:
            return e