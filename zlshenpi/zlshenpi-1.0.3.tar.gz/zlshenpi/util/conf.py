from lmf.dbv2 import db_command, db_write, db_query
import pandas as pd

from os.path import join, dirname


def get_conp(name, database=None):
    path1 = join(dirname(__file__), "cfg_db")
    if database is None:
        df = db_query("select * from cfg where schema='%s' " % name, dbtype='sqlite', conp=path1)
    else:
        df = db_query("select * from cfg where schema='%s' and database='%s' " % (name, database), dbtype='sqlite',
                      conp=path1)
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


def update(user=None, password=None, host=None):
    if host is not None:
        sql = "update cfg set host='%s' " % host
        command(sql)
    if user is not None:
        sql = "update cfg set user='%s' " % user
        command(sql)
    if password is not None:
        sql = "update cfg set password='%s' " % password
        command(sql)


def add_conp(conp):
    sql = "insert into cfg values('%s','%s','%s','%s','%s')" % (conp[0], conp[1], conp[2], conp[3], conp[4])
    command(sql)


def get_df():
    data1 = {
        'shenpi':['guangdongsheng']
    }
    data = []
    print('total', len(data1.values()))
    i = 0
    for w in data1.keys():
        tmp1 = data1[w]
        for w1 in tmp1:
            tmp = ["postgres", "since2015", "192.168.3.171", w, w1]
            print(tmp)
            i += 1
            data.append(tmp)
    print(i)
    df = pd.DataFrame(data=data, columns=["user", 'password', "host", "database", "schema"])
    return df

    return df

# gcjs
# def create_all_schemas():
#     conp = get_conp1('gcjs')
#     for w in data1.keys():
#         tmp1=data1[w]
#         for w1 in tmp1:
#             sql = "create schema if not exists %s" % (w+'_'+w1)
#             db_command(sql, dbtype="postgresql", conp=conp)


df=get_df()
print(len(df),df)
db_write(df,'cfg',dbtype='sqlite',conp=join(dirname(__file__),"cfg_db"))
# #
#
# # add_conp(["postgres","since2015","192.168.4.175",'jiangxi','yichun'])
# # # #
# df = query("select * from cfg")
# print(len(df.values))
# print(df.values)
# 335
