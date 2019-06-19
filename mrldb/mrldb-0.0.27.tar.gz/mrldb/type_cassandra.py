__doc__=f"""mrldb by Rémi "Mr e-RL" LANGDORPH
Copyright (c) 2019 Rémi LANGDORPH - mrerl@warlegend.net
under MIT License (https://github.com/merlleu/mrldb/blob/master/LICENSE)"""
from .struct import get_struct_init

class MrlDBCassandra:
    def __init__(self, cluster, db=None, structure=None, username=None, password=None):
        from cassandra.cqlengine import connection
        from cassandra.cluster import Cluster
        if isinstance(cluster, str):
            cluster=[cluster]
        if (username==None or password==None):
            self.cluster=Cluster(cluster)
        else:
            from cassandra.auth import PlainTextAuthProvider
            self.auth_provider = PlainTextAuthProvider(username=username, password=password)
            self.cluster=Cluster(cluster, auth_provider=self.auth_provider)
        if db!=None:
            self.db=self.cluster.connect(db)
            self.cursor=self.db
        else:
            self.cursor=self.cluster
        self.structure=structure
        self._config={"system":"cassandra", "cluster": cluster,"database": db, "structure": f"{len(structure) if structure!=None else '0'} tables", "username": username, "password":password}
        return
    def insert(self, table, data):
        def frmt(d):
            return f"'{d}'" if isinstance(d, str) else ("null" if d==None else str(d))
        return self.cursor.execute(f"INSERT INTO {table}({', '.join([x for x in data.keys()])}) VALUES ({', '.join([frmt(x) for x in data.values()])})")
    def update(self, table, data, conds=None):
        def frmt(d):
            return f"'{d}'" if isinstance(d, str) else ("null" if d==None else str(d))
        return self.cursor.execute(f"UPDATE {table} SET {', '.join([key+'='+frmt(arg) for key, arg in data.items()])}{' WHERE '+conds if conds!=None else ''}")
    def select(self, table, columns, conds=None):
        if self.structure!=None:
            if columns=="*":columns=self.structure[table].keys()
            return [
            {_col:_var for _col, _var in zip(columns, record)}
            for record in
            self.cursor.execute(f"SELECT {'*' if columns=='*' else ', '.join(columns)} FROM {table}{' WHERE '+conds if conds!=None else ''}")
            ]
        else:
            return self.cursor.execute(f"SELECT {'*' if columns=='*' else ', '.join(columns)} FROM {table}{' WHERE '+conds if conds!=None else ''}")
    def delete(self, table, conds=None):
        # table= "mytable"
        # conds= "(x=1) or (x=2 and y=3)"
        return self.cursor.execute(f"DELETE FROM {table}{' WHERE '+conds if conds!=None else ''}")
    def _getinfos(self):
        return self._config
    def init(self):
        [self.cursor.execute(command) for command in get_struct_init(self.structure)]
        return self
    def __str__(self):
        return f"<mrldb.MrlDBCassandra at {id(self)} - connection: {self._config['cluster']}>"
    def __repr__(self):
        return f"<mrldb.MrlDBCassandra at {id(self)} - connection: {self._config['cluster']}>"
