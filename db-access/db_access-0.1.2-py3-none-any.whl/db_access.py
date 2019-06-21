from sqlalchemy import create_engine as _create_engine, Table as _Table, MetaData as _MetaData
import urllib as _urllib
import abc as _abc
import cx_Oracle as _cx_Oracle
import warnings
from impala.dbapi import connect as _impala_connect


class DatabaseConnection:

    def __init__(self, server, port, user, pw, **kwargs):
        self.server=server
        self.port=port
        self.user=user
        self.pw=pw
        self._meta = _MetaData()
        self.engine=None

    @_abc.abstractmethod
    def create_engine(self):
        pass

    def close_engine(self):
        self.engine.close()

    def get_engine(self):
        if self.engine is None:
            self.create_engine()
        return self.engine
    
    def get_table(self, table_name, schema):
        return _Table(table_name, self._meta, schema=schema, autoload=True, autoload_with=self.engine)


class MSSQLConnection(DatabaseConnection):

    def __init__(self, server, port, database, user, pw):
        super().__init__(server, port, user, pw)
        self.database = database
        self._params = _urllib.parse.quote_plus(
            'DRIVER={ODBC Driver 17 for SQL Server};SERVER=%s,%s;DATABASE=%s;UID=%s;PWD=%s;' % (
                self.server,
                self.port,
                self.database,
                self.user,
                self.pw
            ))

    def create_engine(self):
        self.engine = _create_engine(
            "mssql+pyodbc:///?odbc_connect=%s" % self._params)


class OracleSqlConnection(DatabaseConnection):

    def __init__(self, server, port, user, pw, service_name=None, sid=None):
        super().__init__(server, port, user, pw)
        self.service_name=service_name
        self.sid=sid
        if (self.service_name is not None) & (self.sid is not None):
            warnings.warn('Both service_name and sid are filled. Service name will be used.')
        if self.service_name is not None:
            self._dsn = _cx_Oracle.makedsn(host=self.server, port=self.port, service_name=self.service_name)
        elif self.sid is not None:
            self._dsn = _cx_Oracle.makedsn(host=self.server, port=self.port, sid=self.sid)
        else:
            raise AttributeError('No service_name or sid was specified')

    def create_engine(self):
        self.engine = _create_engine('oracle://' + self.user + ':' + self.pw + '@' + self._dsn)


class ImpalaConnection(DatabaseConnection):

    def __init__(self, server, port, user, pw, database, auth_mechanism):
        super().__init__(server, port, user, pw)
        self.database=database
        self.auth_mechanism = auth_mechanism

    def create_engine(self):
        self.engine = _create_engine('impala://', creator=self._conn)

    def _conn(self):
        impala_connection = _impala_connect(
            host=self.server, 
            port=int(self.port), 
            database=self.database, 
            user=self.user, 
            password=self.pw, 
            auth_mechanism=self.auth_mechanism
        )
        return impala_connection

class MySQLConnection(DatabaseConnection):

    def __init__(self, server, port, user, pw, database):
        super().__init__(server, port, user, pw)
        self.database=database

    def create_engine(self):
        self.engine = _create_engine("mysql+pymysql://{}:{}@{}/{}".format(self.user, self.pw, self.server, self.database))