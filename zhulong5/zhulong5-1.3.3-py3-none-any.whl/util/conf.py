from lmf.dbv2 import db_command, db_write, db_query

from os.path import join, dirname

import pandas as pd


def get_conp(name, database=None):
    path1 = join(dirname(__file__), "cfg_db")
    if database is None:
        df = db_query("select * from cfg where schema='%s' " % name, dbtype='sqlite', conp=path1)
    else:
        df = db_query("select * from cfg where schema='%s' and database='%s' " % (name, database), dbtype='sqlite', conp=path1)
    conp = df.values.tolist()[0]
    return conp


def get_conp1(name):
    path1 = join(dirname(__file__), "cfg_db")

    df = db_query("select * from cfg where database='%s' and schema='public' " % name, dbtype='sqlite', conp=path1)
    conp = df.values.tolist()[0]
    return conp


def command(sql):
    path1 = join(dirname(__file__), "cfg_db")
    db_command(sql, dbtype="sqlite", conp=path1)


def query(sql):
    path1 = join(dirname(__file__), "cfg_db")
    df = db_query(sql, dbtype='sqlite', conp=path1)
    return df


def update(user=None, password=None, host=None,database=None,schema=None):
    if host is not None:
        sql = "update cfg set host='%s' " % host
        command(sql)
    if user is not None:
        sql = "update cfg set user='%s' " % user
        command(sql)
    if password is not None:
        sql = "update cfg set password='%s' " % password
        command(sql)
    if database is not None:
        sql = "update cfg set database='%s' " % database
        command(sql)



def add_conp(conp):
    sql = "insert into cfg values('%s','%s','%s','%s','%s')" % (conp[0], conp[1], conp[2], conp[3], conp[4])
    command(sql)


data1 = {
    'teshu': ['touzishenpi','jianzhu']

}


def get_df():
    data = []
    database = ['anbang','guoziqiang']
    for w in data1.keys():
        tmp1 = data1[w]
        for i,w1 in enumerate(tmp1):
            tmp = ["postgres", "since2015", "192.168.3.171", database[i], w1]
            data.append(tmp)

    df = pd.DataFrame(data=data, columns=["user", 'password', "host", "database", "schema"])
    return df


def create_all_schemas():
    conp = get_conp1('touzishenpi')
    for w in data1.keys():
        tmp1 = data1[w]
        for w1 in tmp1:
            sql = "create schema if not exists %s" % (w1)
            db_command(sql, dbtype="postgresql", conp=conp)

# df=get_df()
# print(df)
# db_write(df,'cfg',dbtype='sqlite',conp=join(dirname(__file__),"cfg_db"))
# #
# add_conp(["postgres","since2015","192.168.4.175",'qycg','public'])
#
# df=query("select * from cfg")
# print(df.values)
