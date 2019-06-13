import json
import time
import pandas as pd
import pymonetdb


class MonetDB:

    def __init__(self, host, port, database, username, password):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password


    def select_metadata(self, schema, table):
        connection = pymonetdb.connect(hostname=self.host, port=self.port, database=self.database,
                                       username=self.username, password=self.password)
        cursor = connection.cursor()
        cursor.arraysize = 1

        cursor.execute('SELECT * FROM %s.%s' % (schema, table))
        metadata = cursor.description
        connection.close()

        columns = []
        for name in metadata:
            columns.append(name[0])

        return columns


    def select(self, schema, table, selection, filter=''):
        start = time.time()
        print('%s Start - Selecting data from %s' % (time.strftime('%H:%M:%S'), table))

        connection = pymonetdb.connect(hostname=self.host, port=self.port, database=self.database,
                                       username=self.username, password=self.password)
        cursor = connection.cursor()
        cursor.arraysize = 10000

        trigger = cursor.execute('SELECT %s FROM %s.%s %s' % (selection, schema, table, filter))

        data = cursor.fetchall()
        connection.close()

        return data


    def insert(self, schema, table, dataframe):
        start = time.time()

        connection = pymonetdb.connect(hostname=self.host, port=self.port, database=self.database, username=self.username, password=self.password)
        cursor = connection.cursor()
        tableHeaders = ', '.join(list(dataframe))
        dataframe = dataframe.reset_index(drop=True)

        values = ','.join(str(index[1:]) for index in dataframe.itertuples())

        print('%s Start inserting data' % (time.strftime('%H:%M:%S')))
        query = 'INSERT INTO %s.%s (%s) VALUES %s' % (schema, table, tableHeaders, values)

        cursor.execute(query)

        connection.commit()
        connection.close()

        print('%s End - Writing data into %s took %f seconds' % (time.strftime('%H:%M:%S'), table, time.time() - start))


    def execute_only(self, query):
        connection = pymonetdb.connect(hostname=self.host, port=self.port, database=self.database,
                                       username=self.username, password=self.password)
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        connection.close()


    def copy_into(self, schema, table, path_to_csv, dataframe, offset=None, field_separator=','):
        # Writes dataframe to local file, copies that to remote file, copies that into database

        # Recording the start-time
        start = time.time()

        # Copy remote file into MonetDB using COPY INTO
        if offset is not None:
            offset = 'OFFSET %s' % (str(offset))
        else:
            offset = ''
        n_rows = '{0} {1} RECORDS'.format(len(dataframe.index), offset)
        column_headers = list(dataframe)

        connection = pymonetdb.connect(hostname=self.host, port=self.port, database=self.database, username=self.username, password=self.password)
        cursor = connection.cursor()

        query = "COPY {0} INTO {1}.{2}({3}) FROM ('{4}') USING DELIMITERS '{5}' NULL AS ''".format(
            n_rows,
            schema,
            table,
            ', '.join(list(column_headers)),
            path_to_csv,
            field_separator
        )
        print(query)
        cursor.execute(query)
        connection.commit()
        connection.close()

        print('%s End - Writing data into %s took %f seconds' % (time.strftime('%H:%M:%S'), schema, time.time() - start))


    def delete(self, schema, table, filter=''):
        start = time.time()
        connection = pymonetdb.connect(hostname=self.host, port=self.port, database=self.database, username=self.username, password=self.password)
        cursor = connection.cursor()
        cursor.execute('DELETE FROM %s.%s %s' % (schema, table, filter))
        connection.commit()
        connection.close()
        print('%s End - Deleting data from %s took %f seconds' % (time.strftime('%H:%M:%S'), table, time.time() - start))


    def create_table(self, schema, table, dataframe):
        start = time.time()
        # Map dataframe datatypes to monetdb datatypes. First in set is dataframe type, second is monetdb.
        datatypes =[
            {'dataframe_type': 'int64', 'monetdb_type': 'INT'},
            {'dataframe_type': 'object', 'monetdb_type': 'VARCHAR(255)'},
            {'dataframe_type': 'float64', 'monetdb_type': 'FLOAT'},
            {'dataframe_type': 'datetime64[ns]', 'monetdb_type': 'TIMESTAMP'},
            {'dataframe_type': 'bool', 'monetdb_type': 'BOOLEAN'}
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
            value = row['columns'] + ' ' + row['monetdb_type']
            headers += ''.join(value) + ', '
        headers = headers[:-2]

        connection = pymonetdb.connect(hostname=self.host, port=self.port, database=self.database,username=self.username, password=self.password)
        cursor = connection.cursor()
        cursor.execute('CREATE TABLE {0}.{1} ({2});'.format(schema, table, headers))
        connection.commit()
        connection.close()

        print('{0} End - Created table {1} in {2} seconds'.format(time.strftime('%H:%M:%S'), table, time.time() - start))



    def drop_table(self, schema, table):
        start = time.time()

        connection = pymonetdb.connect(hostname=self.host, port=self.port, database=self.database, username=self.username, password=self.password)
        cursor = connection.cursor()
        cursor.execute('DROP TABLE IF EXISTS {0}.{1}'.format(schema, table))
        connection.commit()
        connection.close()

        print('{0} - Dropping table {1} took {2} seconds'.format(time.strftime('%H:%M:%S'), table, time.time() - start))