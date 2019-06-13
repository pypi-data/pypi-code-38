#!/usr/bin/env python3

import sqlite3
import pickle
import pandas

class necstdb(object):

    def __init__(self, dbpath, num=1):
        self.dbpath = dbpath
        self.open(self.dbpath)
        self.mk_cur(num)
        pass

    def __del__(self):
        self.con.close()
        return

    def open(self, dbpath):
        self.con = sqlite3.connect(dbpath, check_same_thread=False)
        return
        
    def mk_cur(self, num):
        self.cur = []
        for i in range(num):
            self.cur.append(self.con.cursor())
        return

    def commit_data(self):
        self.con.commit()
        return

    def close(self):
        self.con.close()
        return

    def make_table(self, table_name, param):
        self.con.execute("CREATE table if not exists {} {}".format(table_name, param))
        return

    def write(self, table_name, param, values, cur_num=0, auto_commit = False):
        if len(values) == 1:
            quest = "?"
        else:
            tmp = ""
            quest = ",".join([tmp + "?" for i in range(len(values))])

        val = []
        for i in range(len(values)):
            if type(values[i]) == list:
                val.append(pickle.dumps(values[i]))
            elif type(values[i]) == tuple:
                val.append(pickle.dumps(list(values[i])))
            else:
                val.append(values[i])
        values = tuple(val)

        if auto_commit:
            with self.con:
                self.cur[cur_num].execute("INSERT into {0} {1} values ({2})".format(table_name, param, quest), values)
        else:
            self.cur[cur_num].execute("INSERT into {0} {1} values ({2})".format(table_name, param, quest), values)
        return
        
    def writemany(self, table_name, param, values, cur_num=0, auto_commit = False):
        if len(values[0]) == 1:
            quest = "?"
        else:
            tmp = ""
            quest = ",".join([tmp + "?" for i in range(len(values[0]))])

        if auto_commit:
            with self.con:
                self.cur[cur_num].executemany("INSERT into {0} {1} values ({2})".format(table_name, param, quest), values)
        else:
            self.cur[cur_num].executemany("INSERT into {0} {1} values ({2})".format(table_name, param, quest), values)
        return

    def read(self, table_name, param="*", cur_num=0):
        row = self.cur[cur_num].execute("SELECT {0} from {1}".format(param, table_name)).fetchall()
        if not row == []:
            data = [
                [row[i][j] for i in range(len(row))] 
                    for j in range(len(row[0]))
                    ]
        else : data = []
        
        dat = []
        for i in range(len(data)):
            if type(data[i][0]) == bytes:
                dat.append([pickle.loads(data[i][j]) for j in range(len(data[i]))])
            else:
                dat.append(data[i])

        return dat

    def read_as_pandas(self, table_name):
        df = pandas.read_sql("SELECT * from {}".format(table_name), self.con)
        return df

    def read_pandas_all(self):
        table_name = self.get_table_name()
        datas = [self.read_as_pandas(name) for name in table_name]
        if datas ==[]:
            df_all = []
        else:
            df_all = pandas.concat(datas, axis=1)
        return df_all

    def check_table(self):
        row = self.con.execute("SELECT * from sqlite_master")
        info = row.fetchall()
        return info

    def get_table_name(self):
        name = self.con.execute("SELECT name from sqlite_master where type='table'").fetchall()
        name_list = sorted([name[i][0] for i in range(len(name))])
        return name_list

