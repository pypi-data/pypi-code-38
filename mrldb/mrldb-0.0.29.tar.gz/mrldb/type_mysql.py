__doc__=f"""mrldb by Rémi "Mr e-RL" LANGDORPH
Copyright (c) 2019 Rémi LANGDORPH - mrerl@warlegend.net
under MIT License (https://github.com/merlleu/mrldb/blob/master/LICENSE)"""

from .struct import get_struct_init
try:
    from mysql.connector.errors import OperationalError
except:
    pass
class MrlDBMsql:
    def __init__(self, host, database=None, structure=None, user=None, password=None, autocommit=True):
        import mysql.connector as mariadb
        self.connection = mariadb.connect(host=host, database=database, user=user, password=password)
        self.cursor = self.connection.cursor()
        self.connection.autocommit=autocommit
        self.structure=structure
        self._config={"system":"mysql", "host": host, "database": database, "structure": f"{len(structure) if structure!=None else '0'} tables", "user": user, "password":password, "autocommit": autocommit}
        return
    def restart(self):
        self.cursor.close()
        self.connection.close()
        import mysql.connector as mariadb
        self.connection = mariadb.connect(host=self._config["host"], database=self._config["database"], user=self._config["user"], password=self._config["password"])
        self.cursor = self.connection.cursor()
        self.connection.autocommit=self._config["autocommit"]
    def insert(self, table, data):
        def frmt(d):
            return f"'{d}'" if isinstance(d, str) else ("null" if d==None else str(d))
        try:
            return self.cursor.execute(f"INSERT INTO {table}({', '.join([x for x in data.keys()])}) VALUES ({', '.join([frmt(x) for x in data.values()])})")
        except OperationalError:
            self.restart()
            return self.cursor.execute(f"INSERT INTO {table}({', '.join([x for x in data.keys()])}) VALUES ({', '.join([frmt(x) for x in data.values()])})")
    def update(self, table, data, conds=None):
        def frmt(d):
            return f"'{d}'" if isinstance(d, str) else ("null" if d==None else str(d))
        try:
            return self.cursor.execute(f"UPDATE {table} SET {', '.join([key+'='+frmt(arg) for key, arg in data.items()])}{' WHERE '+conds if conds!=None else ''}")
        except OperationalError:
            self.restart()
            return self.cursor.execute(f"UPDATE {table} SET {', '.join([key+'='+frmt(arg) for key, arg in data.items()])}{' WHERE '+conds if conds!=None else ''}")
    def select(self, table, columns, conds=None, nowrap=False):
        if columns=="*":columns=self.structure[table].keys()
        try:self.cursor.execute(f"SELECT {'*' if columns=='*' else ', '.join(columns)} FROM {table}{' WHERE '+conds if conds!=None else ''}")
        except OperationalError:
            self.restart()
            self.cursor.execute(f"SELECT {'*' if columns=='*' else ', '.join(columns)} FROM {table}{' WHERE '+conds if conds!=None else ''}")
        if not nowrap:
            return [
            {_col:_var for _col, _var in zip(columns, record)}
            for record in
            self.cursor.fetchall()
            ]
        else:
            return self.cursor.fetchall()
    def delete(self, table, conds=None):
        # table= "mytable"
        # conds= "(x=1) or (x=2 and y=3)"
        try:return self.cursor.execute(f"DELETE FROM {table}{' WHERE '+conds if conds!=None else ''}")
        except OperationalError:
            self.restart()
            return self.cursor.execute(f"DELETE FROM {table}{' WHERE '+conds if conds!=None else ''}")
    def _getinfos(self):
        return self._config
    def init(self):
        [self.cursor.execute(command) for command in get_struct_init(self.structure)]
        return self
    def __str__(self):
        return f"<mrldb.MrlDBMsql at {id(self)} - connection: {self._config['host']}>"
    def __repr__(self):
        return f"<mrldb.MrlDBMsql at {id(self)} - connection: {self._config['host']}>"
