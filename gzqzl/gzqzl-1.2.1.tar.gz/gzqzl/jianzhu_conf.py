import json

from lmf.dbv2 import db_command, db_write, db_query
import pandas as pd
from sqlalchemy import create_engine, types
from sqlalchemy.dialects.postgresql import TEXT
from os.path import join, dirname


def get_conp(name, tb_name,dname,database=None):
    path1 = join(dirname(__file__), "%s"%dname)
    if database is None:
        df = db_query("select * from %s where schema='%s' " % tb_name,name, dbtype='sqlite', conp=path1)
    else:
        df = db_query("select * from %s where schema='%s' and database='%s' " % (tb_name,name, database), dbtype='sqlite',conp=path1)
    conp = df.values.tolist()[0]
    return conp


def get_conp1(name, tb_name,dname):
    path1 = join(dirname(__file__), "%s"%dname)

    df = db_query("select * from %s where database='%s' and schema='public' " % tb_name,name, dbtype='sqlite', conp=path1)
    conp = df.values.tolist()[0]
    return conp


def command(sql, dname):
    path1 = join(dirname(__file__), "%s" % dname)
    db_command(sql, dbtype="sqlite", conp=path1)


def query(sql, dname):
    path1 = join(dirname(__file__), "%s" % dname)
    df = db_query(sql, dbtype='sqlite', conp=path1)
    return df


def update(tb_name,dname, total=None, payloadData=None):
    if total is not None:
        sql = "update %s set total='%s' " % tb_name,total
        command(sql, dname)
    if payloadData is not None:
        sql = "update %s set payloadData='%s' " % tb_name,payloadData
        command(sql, dname)


def add_conp(conp, tb_name,dname):
    sql = "insert into %s values('%s','%s')" % (tb_name, conp[0], conp[1])
    command(sql, dname)



def get_df(w1_lsit, tb_name):
    data = []
    n =0
    for w1 in w1_lsit:
        tmp=[w1[0],json.dumps(w1[1],ensure_ascii=False)]
        n+=1
        data.append(tmp)
    print('准备插入%s条数据到%s表'% (n,tb_name))
    df = pd.DataFrame(data=data, columns=["total", 'payloadData'])
    db_write(df, '%s'% tb_name, dbtype='sqlite', conp=join(dirname(__file__), "%s_db"% tb_name))
    print('插入成功！')
    return df




# from os.path import join, dirname
#
# df=get_df()
# db_write(df,'cfg2',dbtype='sqlite',conp=join(dirname(__file__),"cfg_db2"))

def jz_db(tb_name):
    df = query("select * from %s"%tb_name, '%s_db'%tb_name)
    # print(len(df.values))
    print('有%s条数据'% (len(df.values)))
    # print(df.values)
    return df.values.tolist()


# print(jz_db('cfg2'))



# jianzhu
# def create_all_schemas():
#     conp = get_conp1('jianzhu')
#     for w in data1.keys():
#         tmp1=data1[w]
#         for w1 in tmp1:
#             sql = "create schema if not exists %s" % (w+'_'+w1)
#             db_command(sql, dbtype="postgresql", conp=conp)

