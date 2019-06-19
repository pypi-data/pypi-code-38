__doc__=f"""mrldb by Rémi "Mr e-RL" LANGDORPH
Copyright (c) 2019 Rémi LANGDORPH - mrerl@warlegend.net
under MIT License (https://github.com/merlleu/mrldb/blob/master/LICENSE)"""
from .struct import get_struct_init
import threading
from queue import Queue
class MrlDBSqlite:
    def __init__(self, file, structure=None, autocommit=0, debug=False):
        self.structure=structure
        self._config={"system":"sqlite", "file": file, "structure": f"{len(structure) if structure!=None else '0'} tables"}
        self.db=sqlite_dbthread(file, debug)
        self.cursor=self.db
        self.autocommit=None
        if autocommit!=0: self.autocommit=sqlite_autocommit(self.db, autocommit)
        return
    def insert(self, table, data):
        def frmt(d):
            return f"'{d}'" if isinstance(d, str) else ("null" if d==None else str(d))
        return self.db.execute(f"INSERT INTO {table}({', '.join([x for x in data.keys()])}) VALUES ({', '.join([frmt(x) for x in data.values()])})")
    def update(self, table, data, conds=None):
        def frmt(d):
            return f"'{d}'" if isinstance(d, str) else ("null" if d==None else str(d))
        return self.db.execute(f"UPDATE {table} SET {', '.join([key+'='+frmt(arg) for key, arg in data.items()])}{' WHERE '+conds if conds!=None else ''}")
    def select(self, table, columns, conds=None):
        if self.structure!=None:
            if columns=="*":columns=self.structure[table].keys()

            return [
            {_col:_var for _col, _var in zip(columns, record)}
            for record in
            self.db.select(f"SELECT {'*' if columns=='*' else ', '.join(columns)} FROM {table}{' WHERE '+conds if conds!=None else ''}")
            ]
        else:
            return self.db.select(f"SELECT {'*' if columns=='*' else ', '.join(columns)} FROM {table}{' WHERE '+conds if conds!=None else ''}")
    def delete(self, table, conds=None):
        # table= "mytable"
        # conds= "(x=1) or (x=2 and y=3)"
        return self.db.execute(f"DELETE FROM {table}{' WHERE '+conds if conds!=None else ''}")
    def _getinfos(self):
        return self._config
    def init(self):
        [self.db.execute(command) for command in get_struct_init(self.structure)]
        return self
    def __str__(self):
        return f"<mrldb.MrlDBSqlite at {id(self)} - connection: {self._config['file']} - autocommit: {f'{self.autocommit.timing} seconds' if self.autocommit!=None else 'disabled'}>"
    def __repr__(self):
        return f"<mrldb.MrlDBSqlite at {id(self)} - connection: {self._config['file']} - autocommit: {f'{self.autocommit.timing} seconds' if self.autocommit!=None else 'disabled'}>"

class sqlite_dbthread(threading.Thread):
    def __init__(self, db, debug):
        threading.Thread.__init__(self)
        self.db=db
        self.status=True
        self.debug=debug
        self.reqs=Queue()
        self.start()
    def run(self):
        import sqlite3
        cnx = sqlite3.Connection(self.db)
        cursor = cnx.cursor()
        while self.status:
            req, arg, res = self.reqs.get()
            if req=='--close--': break
            elif req=='--commit--': cnx.commit()
            try:
                if self.debug: print(self.db ,"\t",req, arg)
                cursor.execute(req, arg)
                if res:
                    for rec in cursor:
                        res.put(rec)
                    res.put('--no more--')
            except:res.put('--no more--')
        cnx.close()
    def execute(self, req, arg=None, res=None):
        self.reqs.put((req, arg or tuple(), res))
    def select(self, req, arg=None):
        res=Queue()
        self.execute(req, arg, res)
        while True:
            rec=res.get()
            if rec=='--no more--': break
            yield rec
    def commit(self):
    	self.execute("--commit--")
    def close(self):
        self.execute('--close--')
    def stop(self):
        self.status=False
class sqlite_autocommit(threading.Thread):
    def __init__(self, sql, t):
        threading.Thread.__init__(self)
        self._stopevent = threading.Event( )
        self.sql=sql
        self.timing=t
        self.start()
    def run(self):
        lastnbr=0
        idn=0
        while not self._stopevent.isSet():
            self._stopevent.wait(self.timing)
            self.sql.commit()
    def stop(self):
        self._stopevent.set( )
