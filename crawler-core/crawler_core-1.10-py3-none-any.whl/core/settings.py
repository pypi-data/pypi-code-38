__version__ = 2.0

# +----------------------------------------------------------+
# +------------------- Database settings --------------------+
# +----------------------------------------------------------+

config_example = """
# Tab separated values
# TYPE  SERVER  USERNAME    PASSWORD    DATABASE
Oracle	servername	username	password    databasename
MsSql	servername	username	password    databasename
Postgre	servername	username	password    databasename
"""

attrs = ['server', 'database', 'username', 'password']
db_types = {'oracle': 'Oracle', 'mssql': 'MsSql', 'postgre': 'Postgre'}


class Bucket:
    pass


class Dbasic:
    port = 5432
    server = None
    database = None
    username = None
    password = None
    conn_trusted = None
    conn_untrusted = None


class DbConfig:
    """
    Configuration file contains all connection data required to connect.
    Ones instance is initiated it is send as argument data in other database classes
    """
    def __init__(self, path):
        self.path = path
        if path is None:
            raise FileNotFoundError('''Please provide file path for database configuration. 
            Look for details print(core.settings.config_example)''')

        with open(self.path) as f:
            for line in f.readlines():
                params = [param.strip() for param in line.split('\t')]
                if not line.startswith('#') and len(params) is 5:
                    db_type, server, user, password, database = params
                    config = dict(zip(['server', 'username', 'password', 'database'],params[1:]))
                    bucket = Bucket()
                    fill = {setattr(bucket, x, y) for x,y in config.items()}
                    db_type = db_types.get(db_type.lower())
                    setattr(self, db_type, bucket)


class MsSql(Dbasic):
    lib_type = "pymssql"

    def __init__(self, data):

        db_default = getattr(data, 'MsSql').__dict__
        blank_attrs = [x for x in attrs if getattr(self, x) is None]
        [setattr(self, x, db_default.get(x)) for x in blank_attrs]

        if self.lib_type == 'pymssql':
            self.conn_trusted = "mssql+pymssql://{}/{}".format(self.server,self.database)
            self.conn_untrusted = "mssql+pymssql://{0}:{1}@{2}/{3}".format(self.username, self.password, self.server, self.database)

        if self.lib_type == 'pyodbc':
            self.conn_trusted = "mssql+pyodbc:///?odbc_connect=DRIVER%3D%7BSQL+Server%7D%3BSERVER%3D{0}" \
                                "%3BDATABASE%3B{1}%3BTrusted_Connection%3Dyes".format(self.server, self.database)
            self.conn_untrusted = "mssql+pyodbc://{0}:{1}@{2}".format(self.username, self.password, self.server)


class Postgre(Dbasic):
    def __init__(self, data):
        db_default = getattr(data, 'Postgre').__dict__
        blank_attrs = [x for x in attrs if getattr(self, x) is None]
        [setattr(self, x, db_default.get(x)) for x in blank_attrs]

        self.conn_trusted = "postgresql://{0}/{1}".format(self.server, self.database)
        self.conn_untrusted = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(self.username,self.password,self.server,self.port,self.database)


class Oracle(Dbasic):
    def __init__(self, data):
        db_default = getattr(data, 'Oracle').__dict__
        blank_attrs = [x for x in attrs if getattr(self, x) is None]
        [setattr(self, x, db_default.get(x)) for x in blank_attrs]

        self.conn_trusted = 'oracle+cx_oracle://{0}:{1}@{2}:1521'.format(self.username, self.password, self.server)
        self.conn_untrusted = self.conn_trusted
