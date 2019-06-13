"""
Module wrapping database access.
"""
import sys
import logging
import sqlalchemy as sa
import psycopg2

log = logging.getLogger(__name__)

# ********************************************************************************
class AttrDef:

    name=None
    datatype='varchar'

    def __init__(self, name, datatype='varchar'):
        self.name=name
        self.datatype = datatype

    def toSQL(self):
        return "{} {}".format(name, datatype)

# ********************************************************************************
class DBConnection:
    """
    DBConnection wraps an sqlalchemy database connection (currently only postgres through psycopg2).
    """

    def __init__ (self,
                  host='127.0.0.1',
                  user='postgres',
                  port=5432,
                  db='postgres',
                  password=None):
        self.host=host
        self.user=user
        self.port=port
        self.db=db
        self.password=password
        self.engine = None
        self.conn=None
        log.debug("create DBconnection info: %s", self.__dict__)


    # overwrite __getitem__ to allow dictory style access to options
    def __getitem__(self, key):
        if key not in self.__dict__:
            raise AttributeError("No such attribute: " + key)
        return self.__dict__[key]

    def __setitem__(self,key,value):
        if key not in self.__dict__:
            raise AttributeError("No such attribute: " + key)
        self.__dict__[key] = value
    
    def getValidKeys(self):
        return self.__dict__
        
    def getUrl(self):
        url = 'postgresql://{}:{}@{}:{:d}/{}'.format(self.user,
                                                  ('' if self.password is None else self.password),
                                                  self.host,
                                                  self.port,
                                                  self.db)
        log.debug("connection url %s", url)
        return url

    def connect(self):
        try:
            engine = sa.create_engine(self.getUrl(),
                echo=False)
            conn = engine.connect()
            log.debug("connected to DB")
        except Exception as ex:
            print(type(ex))
            print("\n\n",ex.args)
            sys.exit(1)
        return conn

    def getPostgresConnectStr(self):
        connstr = 'host={} port={} dbname={} user={}'.format(self.host,
                                                          self.port,
                                                          self.db,
                                                          self.user)
        connstr += ('' if self.password is None else ' password={}'.format(self.password))
        log.debug("psycopg2 connection string is <%s>", connstr)
        return connstr
    
    def pgconnect(self):
        try:
             self.conn = psycopg2.connect(self.getPostgresConnectStr())
             return self.conn
        except psycopg2.OperationalError as ex:
             log.error('Fail to connect to the database ({})\n\n{}'.format(self.getUrl(), ex.args))
             sys.exit(1)

    
    def close(self):
        if conn is not None:
            conn.close()
            conn = None
        if engine is not None:
            engine.dispose()
        engine=None
        log.debug("closed connection")

    CREATE_TABLE_TEMP = 'CREATE TABLE IF NOT EXISTS {} ({});'

    def createOrReplaceTable(tableName, attrs, constraints):
        if engine is None or conn is None:
            raise SQLException("cannot create table: no database connection")
        stmtStr = CREATE_TABLE_TEMP.format(tableName, ",".join(attrs + constraints))
        conn.execute(stmtStr)


if __name__ =='__main__':
    dbc = DBConnection()
    dbc['local_table'] = 'pub_large_no_domain_local'
    print(dbc['local_table'])
