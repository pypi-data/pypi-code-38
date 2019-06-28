import json
import time
import pandas as pd
import pymysql


class MySQL:

    def __init__(self, host, user, password, database, port=3306):
        self.host = host
        self. user = user
        self.password = password
        self.database = database
        self.port = port


    def raw_query(self, query, insert=False, keep_open=False):
        start = time.time()
        connection = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database, port=self.port)
        cursor = connection.cursor()
        cursor.execute(query)
        if insert:
            connection.commit()
            data = '{0} - Writing data took {1} seconds'.format(time.strftime('%H:%M:%S'), time.time() - start)
        else:
            data = cursor.fetchall()
        connection.close()
        return data


    def update(self, table: str, columns: list, values: list, filter='', keep_open=False):
        start = time.time()
        connection = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database, port=self.port)
        cursor = connection.cursor()
        update_values = ''
        for index in range(len(columns)):
            if index != len(columns) - 1:
                update_values += "`{}` = '{}',".format(columns[index], values[index])
            else:
                update_values += "`{}` = '{}'".format(columns[index], values[index])
        query = "UPDATE `{}` SET {} {};".format(table, update_values, filter)
        print(query)
        cursor.execute(query)
        connection.commit()
        data = '{0} - Updating data took {1} seconds'.format(time.strftime('%H:%M:%S'), time.time() - start)
        connection.close()
        return data


    def select_metadata(self, table, keep_open=False):
        connection = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database, port=self.port)
        cursor = connection.cursor()
        cursor.arraysize = 1
        cursor.execute('SELECT * FROM {0}'.format(table))
        metadata = cursor.description
        connection.close()

        columns = []
        for name in metadata:
            columns.append(name[0])

        return columns


    def select(self, table, selection, filter='', keep_open=False):
        connection = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database, port=self.port)
        cursor = connection.cursor()
        cursor.arraysize = 10000
        cursor.execute('SELECT {0} FROM {1} {2}'.format(selection, table, filter))
        data = cursor.fetchall()
        connection.close()
        return list(data)


    def insert(self, table, dataframe, keep_open=False):
        start = time.time()
        connection = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database, port=self.port)
        cursor = connection.cursor()
        tableHeaders = ', '.join(list(dataframe))
        dataframe = dataframe.reset_index(drop=True)
        values = ','.join(str(index[1:]) for index in dataframe.itertuples())
        values = values.replace('None', 'DEFAULT')
        query = """INSERT INTO {0} ({1}) VALUES {2}""".format(table, tableHeaders, values)
        cursor.execute(query)
        connection.commit()
        connection.close()
        return '{0} - Writing data took {1} seconds'.format(time.strftime('%H:%M:%S'), time.time() - start)


    def delete(self, table, filter='', keep_open=False):
        start = time.time()
        connection = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database, port=self.port)
        cursor = connection.cursor()
        cursor.execute('DELETE FROM {0} {1}'.format(table, filter))
        connection.commit()
        connection.close()
        return '{0} - Deleting data took {1} seconds'.format(time.strftime('%H:%M:%S'), time.time() - start)


    def create_table_if_not_exists(self, table, dataframe, keep_open=False):
        start = time.time()
        # Map dataframe datatypes to monetdb datatypes. First in set is dataframe type, second is monetdb.
        datatypes =[
            {'dataframe_type': 'int64', 'mysql_type': 'INT'},
            {'dataframe_type': 'uint64', 'mysql_type': 'VARCHAR(255)'},
            {'dataframe_type': 'object', 'mysql_type': 'VARCHAR(255)'},
            {'dataframe_type': 'float64', 'mysql_type': 'FLOAT'},
            {'dataframe_type': 'datetime64[ns]', 'mysql_type': 'TIMESTAMP'},
            {'dataframe_type': 'bool', 'mysql_type': 'BOOLEAN'}
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
            value = '`' + row['columns'] + '` ' + row['mysql_type']
            headers += ''.join(value) + ', '
        headers = headers[:-2]

        connection = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database, port=self.port)
        cursor = connection.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS {0} ({1});'.format(table, headers))
        connection.commit()
        connection.close()

        print('{0} End - Created table {1} in {2} seconds'.format(time.strftime('%H:%M:%S'), table, time.time() - start))



    def drop_table(self, schema, table, keep_open=False):
        start = time.time()

        connection = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database, port=self.port)
        cursor = connection.cursor()
        cursor.execute('DROP TABLE IF EXISTS {0}'.format(table))
        connection.commit()
        connection.close()

        print('{0} - Dropping table {1} took {2} seconds'.format(time.strftime('%H:%M:%S'), table, time.time() - start))
