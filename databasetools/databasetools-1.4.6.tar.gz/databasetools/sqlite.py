import _csv
import ast
import sqlite3
from tqdm import tqdm


class SQLiteSyntax:
    def __init__(self, table_name, data, header):
        self.table_name = table_name
        if type(data) == str:
            open_file = open(data, 'r')
            csv_file = _csv.reader(open_file)
            self.data = [row for row in csv_file]
            if header is not None:
                self.data.insert(0, header)
            open_file.close()
            print('\tSQLite input data type: CSV')
        elif type(data) == list:
            if type(data[1]) == str:
                self.data = [d.split('/') for d in data]
            else:
                self.data = data
            self.data.insert(0, header)
            print('\tSQLite input data type: LIST')

    def statement(self):
        table = self.create_table()
        rows = self.insert_into()
        return table, rows

    @staticmethod
    def sqlstr(string):
        return string.replace(' ', '_').lower()

    @staticmethod
    def data_type(val, current_type):
        try:
            # Evaluates numbers to an appropriate type, and strings an error
            t = ast.literal_eval(val)
        except ValueError:
            return 'varchar'
        except SyntaxError:
            return 'varchar'
        if type(t) in [int, float]:
            if (type(t) in [int]) and current_type not in ['float', 'varchar']:
                # Use smallest possible int type
                if (-32768 < t < 32767) and current_type not in ['int', 'bigint']:
                    return 'smallint'
                elif (-2147483648 < t < 2147483647) and current_type not in ['bigint']:
                    return 'int'
                else:
                    return 'bigint'
            if type(t) is float and current_type not in ['varchar']:
                return 'decimal'
        else:
            return 'varchar'

    def create_table(self):
        longest, headers, type_list = [], [], []
        for row in self.data:
            if len(headers) == 0:
                headers = []
                for i in row:
                    headers.append(self.sqlstr(i))
                for col in row:
                    longest.append(0)
                    type_list.append('')
            else:
                for i in range(len(row)):
                    # NA is the csv_tools null value
                    if type_list[i] == 'varchar' or row[i] == 'NA':
                        pass
                    else:
                        var_type = self.data_type(row[i], type_list[i])
                        type_list[i] = var_type
                    if len(row[i]) > longest[i]:
                        longest[i] = len(row[i])

        statement = 'create table IF NOT EXISTS ' + self.table_name + ' ('

        def str_replace(string):
            return string.replace(' ', '_').replace('/', 'per').lower()

        for i in range(len(headers)):
            if type_list[i] == 'varchar':
                statement = (statement + '\n\t{} varchar({}),').format(str_replace(headers[i]), str(longest[i]))
            else:
                statement = (statement + '\n\t' + '{} {}' + ',').format(str_replace(headers[i]), type_list[i])

        statement = statement[:-1] + '\n);'
        return statement

    def insert_into(self):
        statements = []
        headers = []
        for row in self.data:
            if len(headers) == 0:
                for i in row:
                    headers.append(self.sqlstr(i))
                insert = 'INSERT INTO ' + self.table_name + ' (' + ", ".join(headers) + ") VALUES "
            else:
                values = map((lambda x: '"' + x + '"'), row)
                statements.append(insert + "(" + ", ".join(values) + ");")
        return statements


class SQLiteQuery:
    def __init__(self, filepath):
        try:
            self.conn = sqlite3.connect(filepath)
            self.c = self.conn.cursor()
            print('\tSQLite DB connection established')
        except sqlite3.OperationalError:
            print('\nError: SQLite DB connection established')

    def disconnect(self):
        self.c.close()
        self.conn.close()

    def create(self, statement):
        try:
            self.c.execute(statement)
            self.conn.commit()
            print('\tSQLite DB table created')
        except sqlite3.OperationalError:
            print('\nError: SQLite DB OperationalError while creating a table')
            print('\tStatement: ' + str(statement))

    def insert(self, statement):
        self.conn.commit()
        errors = []
        for each in tqdm(statement, 'Inserting Rows'):
            try:
                self.c.execute(each)
                self.conn.commit()
            except:
                errors.append(str('\tError: ') + ": " + str(each))

        print("\tSQLite DB insert errors:")
        for e in errors:
            print('\t' + e)
        print('\tSQLite rows successfully inserted')

    def insert_many(self, table_name, data, header):
        # Convert header (list of column names) to string
        cols_str = ""
        vals_str = ""
        for h in header:
            cols_str = cols_str + h + ', '
            vals_str = vals_str + '?' + ', '
        cols_str = cols_str[:-2]
        vals_str = vals_str[:-2]

        # Concatenate query
        query = "INSERT INTO " + table_name + " (" + cols_str + ") " + "VALUES (" + vals_str + ")"
        try:
            self.c.executemany(query, data)
            self.conn.commit()
            print('\tSQLite rows succesfully inserted')
        except sqlite3.OperationalError:
            print('\tError: SQLite rows not inserted')

    def truncate(self, table_name):
        self.c.execute("SELECT * FROM " + str(table_name) + ";")
        row = self.c.fetchone()
        try:
            if len(row) is not 0:
                try:
                    self.c.execute("DELETE FROM " + str(table_name) + ";")
                    self.conn.commit()
                    print('\tSQLite DB truncating ' + str(table_name))
                except sqlite3.OperationalError:
                    print('\tError: SQLite DB OperationalError while truncating table_name')
        except TypeError:
            print('\tException: SQLite table ' + str(table_name) + ' is already empty, could not be truncated')


class SQLiteTools:
    def __init__(self, db_filepath, table_name, data, header):
        self.db_filepath = db_filepath
        self.table_name = table_name
        self.data = data
        self.header = header
        self.update_table()

    def update_table(self):
        db_filepath = str(self.db_filepath)
        # Generate SQL statements
        create_tbl, insert_rows = SQLiteSyntax(self.table_name, self.data, self.header).statement()
        sql = SQLiteQuery(db_filepath)  # Connect to SQLite database

        # Remove first item from data list
        self.data.pop(0)

        # Create table if not exist
        sql.create(create_tbl)

        # Truncate table if exists
        sql.truncate(self.table_name)

        # Insert rows
        if len(self.data) == 1:
            sql.insert(insert_rows)
        else:
            sql.insert_many(self.table_name, self.data, self.header)

        # Disconnect
        sql.disconnect()
