from clickhouse_driver import Client

class Clickhouse:
    def __init__(self, host, database, user, password, port=9000):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    def insert(self, table, df):

        client = Client(self.host, database=self.database, user=self.user, password=self.password, port=self.port, verify=False)
        # table_headers = ', '.join(list(df))
        # df = df.reset_index(drop=True)
        # values = ','.join(str(index[1:]) for index in df.itertuples())
        # query = 'INSERT INTO {0}.{1} ({2}) VALUES {3}'.format(self.database, table, table_headers, values)
        # final_query = ''
        # for i in range(len(query)):
        #     if (query[i] == '\''):
        #         final_query += '\\' + query[i]
        #     else:
        #         final_query += query[i]
        # print(final_query)
        #
        # response = client.execute(final_query)
        # return response

        # table_headers = ', '.join(list(df))
        # query = 'INSERT INTO {0}.{1} ({2}) VALUES'.format(self.database, table, table_headers)
        # values = [{list(df)[i]: df.iloc[:, i].tolist()} for i in range(len(list(df)))]
        # values = []
        # for i in range(len(list(df))):
        #     values.append('(' + ', '.join('\'' + str(x) + '\'' for x in df.iloc[:, i].tolist()) + ')')
        # values = ', '.join(values)
        # print(query + ' ' + values)
        # print(client.execute(query + ' ' + values + ';', columnar=False, with_column_types=True, types_check=False))

        table_headers = ', '.join(list(df))
        values = ''
        print('hier')
        for i in list(df):
            if i == list(df)[-1]:
                values += ("('" + "','".join(map(str, df[i].values[0:10])) + "')")
            else:
                values += ("('" + "','".join(map(str, df[i].values[0:10])) + "'),")
        print('hier2')
        print(values)
        # query = 'INSERT INTO {0}.{1} ({2}) VALUES {3}'.format(self.database, table, table_headers, values)
        # query = "INSERT INTO {0} ({1}) VALUES {2}".format(table, table_headers, values)
        #     [{'x': 1}, {'x': 2}, {'x': 3}, {'x': 100}]
        # query = 'INSERT INTO d4w_bi_functie (begindatum_functie, contract_nr, dienstverband_nr, dienstverband_volg_nr, einddatum_functie, functie, functie_id, functiegroep, functiegroep_id, last_modified, leidinggevende, leidinggevende_id, medewerker_id_temp, last_modified_time) VALUES ('2016-11-1')'

        # TODO: turn values into {column_1: [1,2,3], column_2: ['a','b','c'], etc...}
        query = "INSERT INTO d4w_bi_functie ({0}) VALUES [{'begindatum_functie': '2016-11-1'}]".format(table_headers)
        # print('Values = ', values)
        # print('Query = ', query)
        print(client.execute(query))

        # table_headers = ', '.join(list(df))
        # query = 'INSERT INTO {0}.{1} ({2}) VALUES'.format(self.database, table, table_headers)
        # values = []
        # print(df.shape)
        # for row in df.iterrows():
        #     index, data = row
        #     values.append(data.tolist())
        #
        # print(values)
        # for i in range(len(values)):
        #     values[i] = '(' + ', '.join(str(x) for x in values[i]) + ')'
        # print(values)
        # values = ', '.join(values)
        # print(values)
        # print(query + ' ' + values)
        # print(client.execute(query + ' ' + values))

    def select(self, table, selection, group_by, limit=0):
        try:
            client = Client(self.host, database=self.database, user=self.user, password=self.password, port=self.port, verify=False)
            limit = 'LIMIT {0}'.format(limit) if limit != 0 else ''
            query = 'SELECT {0} FROM {1}.{2} {3} GROUP BY {4}'.format(selection, self.database, table, limit, group_by)
            response = client.execute(query, with_column_types=True)

            client.disconnect()
            headers = [response[1][i][0] for i in range(len(response[1]))]
            data = response[0]

            # Returns a list of two lists: headers, data
            response = ['', '']
            response[0] = headers
            response[1] = data
            return response

        except Exception as e:
            return e

    def query(self, query):
        try:
            client = Client(self.host, database=self.database, user=self.user, password=self.password, port=self.port, verify=False)
            query = query
            response = client.execute(query, with_column_types=True)
            client.disconnect()

            headers = [response[1][i][0] for i in range(len(response[1]))]
            data = response[0]

            # Returns a list of two lists: headers, data
            response = ['', '']
            response[0] = headers
            response[1] = data
            return response

        except Exception as e:
            return e

    def show_tables(self):
        client = Client(self.host, database=self.database, user=self.user, password=self.password, port=self.port, verify=False)
        print(client.execute('SHOW TABLES FROM {0}'.format(self.database)))
        client.disconnect()

    def get_column_headers(self, table):
        pass
