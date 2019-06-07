import re
import sqlalchemy
import sqlalchemy.engine
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Table
from sqlalchemy.sql.expression import insert, select, update, delete
from sqlalchemy.sql.expression import text as text_statement
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from psycopg2.extensions import QuotedString as SqlString

import urllib

try:
    import itertools.imap as map
except ImportError:
    pass

try:
    text = unicode
except NameError:
    text = str


#TODO: Lazy session !!!
#NOTE: Lazy sessions are problematic. potentionaly require log running connections
# with open cursor blocking reloads of tables. Solution: timeouts client/server side
# caching, throtling

def get_value(data, keys, default=None):
    result = None

    for k in keys:
        result = data.get(k)

        if result is not None:
            return result

    if result is None:
        return default


def create_engine(params):

    db_type = get_value(params, ['type', 'db_type'], 'pgsql')
    default_port = None

    if db_type == 'mysql':
        default_port = 3306

    elif db_type == 'pgsql':
        default_port = 5432

    elif db_type == 'mssql':
        default_port = 1433

    ctx = (get_value(params, ['user']),
           get_value(params, ['passwd', 'password', 'pass']),
           get_value(params, ['host', 'server'], 'localhost'),
           get_value(params, ['port'], default_port),
           get_value(params, ['database', 'db_name', 'database_name', 'db']))

    #TODO: harmonize, use quoting
    if db_type == 'pgsql':
        url = 'postgresql+psycopg2://%s:%s@%s:%s/%s' % ctx

    elif db_type == 'mysql':
        url = 'mysql+mysqldb://%s:%s@%s:%s/%s' % ctx

    elif db_type == 'mssql':
        url = 'mssql+pyodbc://%s:%s@%s:%s/%s?driver=SQLServer13' % ctx


    else:
        raise ValueError('db_type must be eighter "mysql"/"pgsql"/"mssql"')

    engine = sqlalchemy.create_engine(url, implicit_returning=True)
    return engine


def preprocess_table_data(table, data):

    if isinstance(data, dict):
        data = [data]

    def convert(item):
        result = {}
        for column in table.columns:
            key = column.name
            value = item.get(text(key))

            if value is not None:
                result[key] = value

        return result

    return list(map(convert, data))


def build_pkey_condition(table, data):
    pkeys = table.primary_key.columns
    condition = []

    for column in pkeys:
        condition.append(column == data[column.name])

    return and_(*condition)


def build_condition_from_dict(table, dict_condition):
    condition = []

    for key,value in dict_condition.items():
        column = getattr(table.columns, key)
        condition.append(column == value)

    return and_(*condition)


def build_order_from_list(table, order_list):

    def get_column(key, direction):

        if direction is not None and direction not in ('desc', 'asc'):
            raise ValueError("Order direction must be 'desc' or 'asc'")

        if direction == 'desc':
            return getattr(table.columns, key).desc()

        else:
            return getattr(table.columns, key)

    def interpret_column(column):

        if isinstance(column, tuple):
            return get_column(column[1], column[0])

        if isinstance(column, str) or isinstance(column, text):
            return get_column(column, 'asc')

        else:
            raise ValueError('Can not interpret order statement. Use list of strings or tuples.')

    if isinstance(order_list, list):
        return list(map(interpret_column, order_list))

    else:
        return [interpret_column(order_list)]



class SqlSessionNotFound(Exception):
    pass


class SqlSessionTooMany(Exception):
    pass


class NoticeCollector(object):

    def __init__(self):
        self.buf = []
        self.callback = None

    def append(self, message):
        message = message.rstrip()

        if self.callback is not None:
            self.callback(message)

        self.buf.append(message)
        if len(self.buf) > 50:
            self.buf.pop(0)

    def __iter__(self):
        return iter(self.buf)


class SqlSession(object):

    def __init__(self, param = None, as_role=None):

        self.column_names = None
        self.transaction = None
        self.as_role = as_role
        self.database_type = 'pgsql'
        self.disposable = False

        if isinstance(param, sqlalchemy.engine.Engine):
            self.engine = param
            self.metadata = sqlalchemy.MetaData(self.engine)

        else:
            self.database_type = get_value(param, ['type', 'db_type'], 'pgsql')
            self.engine = create_engine(param)
            self.metadata = sqlalchemy.MetaData(self.engine)
            self.disposable = True


    def __enter__(self):
        self.connection = self.engine.connect()

        if self.database_type == 'pgsql':
            self.connection.connection.connection.notices = NoticeCollector()

        if self.as_role is not None:
            self.set_role(self.as_role)

        return self

    def __exit__(self, type, value, traceback):
        if self.transaction is not None:
            self.transaction.commit()
            self.transaction = None

        self.connection.close()
        if self.disposable:
            self.engine.dispose()

    def begin(self):
        self.transaction = self.connection.begin()

    def end(self):
        if self.transaction is not None:
            self.transaction.commit()
            self.transaction.close()
            self.transaction = None

    def rollback(self):
        if self.transaction is not None:
            self.transaction.rollback()
            self.transaction.close()
            self.transaction = None

    def execute(self, statement):

        #if isinstance(statement, text):
        #    statement = text_statement(statement)

        if self.transaction is not None:
            return self.connection.execute(statement)

        else:
            result = self.connection.execute(statement)
            self.connection.execute('commit;')
            return result

    def commit(self):
        if self.transaction is not None:
            self.transaction.commit()
            self.transaction = None
        else:
            self.connection.execute('commit;')

    def get_unbound_connection(self):
        return self.engine.contextual_connect(close_with_result=True).execution_options(stream_results=True)

    def get_table(self, schema_table_name):
        t = schema_table_name.split('.')

        if len(t) == 1:
            table_name = t[0]
            return Table(table_name, self.metadata, autoload=True,
                         autoload_with=self.engine)

        elif len(t) == 2:
            schema_name, table_name = t
            return Table(table_name, self.metadata, autoload=True,
                         autoload_with=self.engine,
                         schema=schema_name)

        else:
            raise ValueError("schema_table_name")

    def update(self, table, data, condition=None):

        if isinstance(table, str):
            table = self.get_table(table)

        if condition is None:
            condition = build_pkey_condition(table, data)

        elif isinstance(condition, dict):
            condition = build_condition_from_dict(table, condition)

        data = preprocess_table_data(table, data)
        stmt = update(table).where(condition).values(data[0])
        return self.execute(stmt)

    def insert(self, table, data):

        if isinstance(table, str):
            table = self.get_table(table)

        data = preprocess_table_data(table, data)
        stmt = insert(table, list(data), returning=table.primary_key.columns)
        return self.execute(stmt)

    def delete(self, table, condition=None):

        if isinstance(table, str):
            table = self.get_table(table)

        if isinstance(condition, dict):
            condition = build_condition_from_dict(table, condition)
            stmt = delete(table).where(condition)
            return self.execute(stmt)

    def truncate(self, table):
        raise RuntimeError('Not yet inmplement')

    def get_statement(self, table, condition, order):

        if isinstance(table, str) or isinstance(table, unicode):
            table = self.get_table(table)

        stmt = table.select()

        if isinstance(condition, dict):
            condition = build_condition_from_dict(table, condition)

        if condition is not None:
            stmt = stmt.where(condition)

        if order is not None:
            stmt = stmt.order_by(*build_order_from_list(table, order))

        return stmt

    def fetch_one(self, table, condition):
        if isinstance(table, str) or isinstance(table, unicode):
            table = self.get_table(table)

        stmt = table.select()

        if isinstance(condition, dict):
            condition = build_condition_from_dict(table, condition)

        if condition is not None:
            stmt = stmt.where(condition)

        return self.one(stmt)

    def fetch_all(self, table, condition=None, order=None):
        stmt = self.get_statement(table, condition, order)
        return self.all(stmt)

    def iter_all(self, table, condition=None, order=None):
        stmt = self.get_statement(table, condition, order)
        connection = self.get_unbound_connection()
        data = connection.execute(stmt)
        result = map(dict, data)
        return result

    def count(self, table, condition):

        if isinstance(table, str) or isinstance(table, unicode):
            table = self.get_table(table)

        if isinstance(condition, dict):
            condition = build_condition_from_dict(table, condition)

        stmt = select([func.count('*')]).where(condition)
        data = self.connection.execute(stmt)
        data = list(data)[0][0]
        return data

    def one(self, statement):
        data = self.connection.execute(statement)
        self.column_names = data.keys()
        data = list(map(dict, data))

        if len(data) > 1:
            raise SqlSessionTooMany("Expected exaclty one record, %s found" % len(data))

        elif len(data) == 0:
            raise SqlSessionNotFound("Row not found")

        return data[0]

    def all(self, statement):
        data = self.connection.execute(statement)
        self.column_names = data.keys()
        result = list(map(dict, data))
        return result


    def drop_table(self, table):
        if isinstance(table, str):
            table = self.get_table(table)

        table.drop()

    def exists(self, table):
        return self.engine.dialect.has_table(self.engine, table)

    def get_current_timestamp(self):
        statement = 'SELECT current_timestamp AS now;'
        return self.one(statement)['now']

    def get_local_timestamp(self):
        statement = 'SELECT localtimestamp AS now;'
        return self.one(statement)['now']

    def set_log_callback(self, callback):
        if self.database_type == 'pgsql':
            self.connection.connection.connection.notices.callback = callback

    def add_user(self, user_name):
        if not re.match('[a-zA-Z0-9_]*', user_name):
            raise ValueError('User name can contain only letters and numbers')

        self.execute('CREATE USER %s' % user_name)

    def add_group(self, group_name):
        if not re.match('[a-zA-Z0-9_]*', group_name):
            raise ValueError('Group name can contain only letters and numbers')

        self.execute('CREATE GROUP %s' % group_name)

    def rename_user(self, old_user_name, new_user_name):

        if not re.match('[a-zA-Z0-9_]*', old_user_name):
            raise ValueError('Old user name can contain only letters and numbers')

        if not re.match('[a-zA-Z0-9_]*', new_user_name):
            raise ValueError('New user name can contain only letters and numbers')

        self.execute('ALTER USER %s RENAME TO %s;' % (old_user_name, new_user_name))

    def rename_group(self, old_group_name, new_group_name):

        if not re.match('[a-zA-Z0-9_]*', old_group_name):
            raise ValueError('Old group name can contain only letters and numbers')

        if not re.match('[a-zA-Z0-9_]*', new_group_name):
            raise ValueError('New group name can contain only letters and numbers')

        self.execute('ALTER GROUP %s RENAME TO %s;' % (old_group_name, new_group_name))

    def add_user_to_group(self, user_name, group_name):
        if not re.match('[a-zA-Z0-9_]*', user_name):
            raise ValueError('User name can contain only letters and numbers')

        if not re.match('[a-zA-Z0-9_]*', group_name):
            raise ValueError('Group name can contain only letters and numbers')

        self.execute('ALTER GROUP %s ADD USER %s' % (group_name, user_name))

    def drop_user_from_group(self, user_name, group_name):
        if not re.match('[a-zA-Z0-9_]*', user_name):
            raise ValueError('User name can contain only letters and numbers')

        if not re.match('[a-zA-Z0-9_]*', group_name):
            raise ValueError('Group name can contain only letters and numbers')

        self.execute('ALTER GROUP %s DROP USER %s' % (group_name, user_name))

    def drop_user(self, user_name):
        if not re.match('[a-zA-Z0-9_]*', user_name):
            raise ValueError('User name can contain only letters and numbers')

        self.execute('DROP USER %s' % user_name)

    def drop_group(self, group_name):
        if not re.match('[a-zA-Z0-9_]*', group_name):
            raise ValueError('User name can contain only letters and numbers')

        self.execute('DROP GROUP %s' % group_name)

    def set_role(self, user_name):
        if not re.match('[a-zA-Z0-9]*', user_name):
            raise ValueError('User name can contain only letters and numbers')

        self.execute('SET role=%s' % user_name)

    def grant_role(self, user_name, target_role):

        if not re.match('[a-zA-Z][a-zA-Z0-9_]*', user_name):
            raise ValueError('User name can contain only letters and numbers')

        if not re.match('[a-zA-Z0-9_]*', target_role):
            raise ValueError('Target role can contain only letters and numbers')
            
        self.execute('GRANT %s TO %s;'  % (user_name, target_role))

    def set_user_password(self, user_name, password):
        if not re.match('[a-zA-Z0-9]*', user_name):
            raise ValueError('User name can contain only letters and numbers')
        
        #TODO: 
        escaped_passord = SqlString(password)
        escaped_passord.encoding = 'utf-8'

        self.execute("ALTER USER %s WITH PASSWORD %s;" % (user_name, escaped_passord))
