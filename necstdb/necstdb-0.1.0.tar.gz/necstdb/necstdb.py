#!/usr/bin/env python3

import os
import sqlite3
import pickle
import pandas

class necstdb(object):

    def __init__(self):
        self.con = None
        self.cur = None
        self.db_path = ''
        pass

    def open(self, db_path):
        self.db_path = db_path
        self.con = sqlite3.connect(db_path, check_same_thread=False)
        self.con.execute("CREATE table if not exists 'necst' ('topic', 'time', 'msgs')")
        self.cur = self.con.cursor()
        return
        
    def commit_data(self):
        self.con.commit()
        return

    def close(self):
        self.con.close()
        self.db_path = ''
        self.con = None
        self.cur = None
        return

    def write(self, values, auto_commit = False):
        table_name = 'necst'
        quest = "?, ?, ?"
        param = ('topic', 'time', 'msgs')
        val = []
        val.append(values['topic'])
        val.append(values['time'])
        val.append(pickle.dumps(values['msgs']))
        values = tuple(val)
        self.cur.execute("INSERT into {0} {1} values ({2})".format(table_name, param, quest), values)
        return
    
    def read(self, param="*"):
        table_name = 'necst'
        self.cur.execute("SELECT {0} from {1}".format(param, table_name))
        ret = []
        for row in self.cur.fetchall():
            dic = dict(zip([d[0] for d in self.cur.description], row))
            dic['msgs'] = pickle.loads(dic['msgs'])
            ret.append(dic)
        return ret
    
    def read_as_pandas(self):
        table_name = 'necst'
        ret = pandas.read_sql("SELECT * from {}".format(table_name), self.con)
        for i in ret.index:
            ret.at[i, 'msgs'] = [pickle.loads(ret['msgs'][i])]
        return ret

    def check_table(self):
        self.cur.execute("SELECT * from sqlite_master")
        ret = self.cur.fetchall()
        return ret

    def get_table_name(self):
        self.cur.execute("SELECT name from sqlite_master where type='table'")
        ret = sorted([i[0] for i in self.cur.fetchall()])
        return ret


###=== for necst-core/logger ===###

    def insert(self, dic):
        if self.con is None:
            self.db_path = dic['path']
            if os.path.exists(self.db_path[:self.db_path.rfind('/')]): pass
            else: os.makedirs(self.db_path[:self.db_path.rfind('/')])
            self.open(self.db_path)
        else:
            if dic['path'] != self.db_path:  
                self.finalize()
                if os.path.exists(self.db_path[:self.db_path.rfind('/')]): pass
                else: os.makedirs(self.db_path[:self.db_path.rfind('/')])
                self.open(dic['path'])
            else: pass
        self.write(dic['data'])
        return

    def finalize(self):
        if self.con is None: pass
        else:
            self.commit_data()
            self.close()
        return

