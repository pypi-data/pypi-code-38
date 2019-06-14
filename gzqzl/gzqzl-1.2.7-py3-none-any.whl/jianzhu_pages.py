import sqlite3

import MySQLdb
import cx_Oracle
import pymssql
import pandas as pd
from sqlalchemy import create_engine
import psycopg2




def db_query(sql, dbtype='mssql', pool=0, conp=None):
    if dbtype == 'mssql':
        con = create_engine("mssql+pymssql://%s:%s@%s/%s" % (conp[0], conp[1], conp[2], conp[3]), encoding='utf-8')
    elif dbtype == 'postgresql':
        con = create_engine("postgresql://%s:%s@%s/%s" % (conp[0], conp[1], conp[2], conp[3]), encoding='utf-8')
        if len(conp) == 4: conp.append('public')
        sql = "set search_path to %s;" % conp[4] + sql
    elif dbtype == 'oracle':
        con = create_engine('oracle://%s:%s@%s/%s' % (conp[0], conp[1], conp[2], conp[3]), encoding='utf-8')
    elif dbtype == 'sqlite':
        con = create_engine('sqlite:///%s' % conp)

    else:
        con = create_engine('mysql://%s:%s@%s/%s?charset=utf8' % (conp[0], conp[1], conp[2], conp[3]), encoding='utf-8')

    df = pd.read_sql(sql, con)
    return df

def db_command(sql,dbtype='mssql',pool=0,conp=None):

    """db_command 仅仅到数据库"""
    # if conp is None:conp=_pool[dbtype][pool]
    if dbtype=='postgresql':
        con=psycopg2.connect(user=conp[0], password=conp[1], host=conp[2], port="5432",database=conp[3])
    elif dbtype=='mssql':
        con=pymssql.connect(user=conp[0], password=conp[1], host=conp[2],database=conp[3])
    elif dbtype=='oracle':
        con = cx_Oracle.connect("%s/%s@%s/%s"%(conp[0],conp[1],conp[2],conp[3]))

    elif dbtype=='sqlite':
        con=sqlite3.connect(conp)
    else:
        con = MySQLdb.connect(user=conp[0],passwd=conp[1],host=conp[2],db=conp[3])
    cur=con.cursor()
    cur.execute(sql)
    con.commit()
    cur.close()
    con.close()


# 保存四库一平台中的多页数据
def jianzhu_insert_pages(conp, data):
    sql = """select table_name from information_schema.tables where table_schema='%s'""" % (conp[4])
    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df["table_name"].values

    if "jianzhu_info_data" in arr:
        conp.append('jianzhu_info_data')
        pages_write(conp, data)
    else:
        insert_work(conp,data)


# 查询表数据
def jianzhu_select_pages(conp, link):
    sql = """select table_name from information_schema.tables where table_schema='%s'""" % (conp[4])
    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df["table_name"].values

    if "jianzhu_info_data" not in arr:
        return []
    conp.append('jianzhu_info_data')
    if link == 0:
        print("数据为空,任务结束")
        return False
    sql1 = """select link,pages from %s.%s where link='%s'""" % (conp[4], conp[5], link)
    df = db_query(sql1, dbtype="postgresql", conp=conp)
    arr = df["pages"].values.tolist()
    return arr


def insert_work(conp, data):
    tb = 'jianzhu_info_data'
    sql = """create table if not exists %s.%s(link text,pages text)""" % (conp[4], tb)
    db_command(sql, dbtype="postgresql", conp=conp)
    print("创建表if不存在")
    conp.append(tb)
    pages_write(conp, data)


def pages_write(conp, data):
    dbtype = "postgresql"
    if dbtype == 'postgresql':
        con = psycopg2.connect(user=conp[0], password=conp[1], host=conp[2], port="5432", database=conp[3])
    elif dbtype == 'mssql':
        con = pymssql.connect(user=conp[0], password=conp[1], host=conp[2], database=conp[3])
    elif dbtype == 'oracle':
        con = cx_Oracle.connect("%s/%s@%s/%s" % (conp[0], conp[1], conp[2], conp[3]))
    else:
        con = MySQLdb.connect(user=conp[0], passwd=conp[1], host=conp[2], db=conp[3])

    if data == 0:
        print("数据为空,任务结束")
        return False
    sql = """insert into %s.%s (link,pages) values ($lmf$%s$lmf$,$lmf$%s$lmf$)
    """ % (conp[4], conp[5], data[0], data[1])
    cur = con.cursor()
    cur.execute(sql)
    con.commit()
    cur.close()
    con.close()



# 对jianzhu_info_data数据去重
def removal_pages_data(conp):
    schema = conp[4]
    sql3 = """
        delete from %s.jianzhu_info_data where ctid in (
        select ctid from
        (select row_number() over(partition by link,pages order by ctid) as rn,ctid from %s.jianzhu_info_data)as t where t.rn<>1)
    """% (schema, schema)
    db_command(sql3, dbtype="postgresql", conp=conp)
