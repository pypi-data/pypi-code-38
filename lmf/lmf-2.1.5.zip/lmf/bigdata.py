import pandas as pd 
from sqlalchemy import create_engine,types
from sqlalchemy.dialects.postgresql import TEXT 
import pymssql
import cx_Oracle
import psycopg2 
import MySQLdb
import datetime
import re
import sqlite3
import os 
from lmf.dbv2 import db_write,db_query
import copy
import traceback
#postgresql 查询结果输出csv文件
def pg2csv(sql,conp,path,**krg):

    para={
    "chunksize":1000,
    "f":None
    }
    para.update(krg)
    chunksize=para["chunksize"]
    f=para["f"]
    krg1=copy.deepcopy(para)
    for w in ["f"]:krg1.pop(w)
    con=create_engine("postgresql://%s:%s@%s/%s"%(conp[0],conp[1],conp[2],conp[3]),encoding='utf-8',execution_options=dict(stream_results=True))
    dfs=pd.read_sql(sql,con,chunksize=chunksize)

    count=1
    for df in dfs:

        total=count*chunksize
        print('第%d行写入中'%total)
        if f is not None:
            df=f(df)
        if count==1:
            df.to_csv(path,index=False,**krg1)
        else:
            krg1['header']=False
            df.to_csv(path,mode='a+',index=False,**krg1)
        count+=1
    if count==1:
        print("df为空")
        df=db_query(sql,dbtype="postgresql",conp=conp)
        df.to_csv(path,index=False,**krg1)



def pg2pg(sql,tb,conp1,conp2,chunksize=100,f=None,if_exists='replace',datadict='postgresql-text'):
    conp=conp1
    con=create_engine("postgresql://%s:%s@%s/%s"%(conp[0],conp[1],conp[2],conp[3]),encoding='utf-8',execution_options=dict(stream_results=True))
    dfs=pd.read_sql(sql,con,chunksize=chunksize)
    count=1
    for df in dfs:
        try:
            total=count*chunksize
            print('第%d行写入中'%total)
            if f is not None:
                df=f(df)
            if count==1:
                db_write(df,tb,dbtype="postgresql",conp=conp2,if_exists=if_exists,datadict=datadict)
            else:
                #krg['header']=False
                db_write(df,tb,dbtype="postgresql",conp=conp2,if_exists='append',datadict=datadict)
            count+=1
        except:
            traceback.print_exc()


def csv2pg(path,conp,**krg):

    para={
    "chunksize":1000,
    "tb":os.path.split(path)[1].replace('.csv',''),
    "f":None,
    "if_exists":"replace",
    "sep":"\001",
    "datadict":"postgresql-text"

    }
    para.update(krg)

    chunksize=para['chunksize']
    f=para['f']
    if_exists=para['if_exists']
    datadict=para["datadict"]
    tb=para['tb']
    para1=copy.deepcopy(para)

    for w in ['datadict','f','if_exists','tb']:
        para1.pop(w)
    dfs=pd.read_csv(path,**para1)
    count=1


    for df in dfs:
        total=count*chunksize
        print('第%d行写入中'%total)
        if f is not None:
            df=f(df)
        if count==1:
            db_write(df,tb,dbtype="postgresql",conp=conp,if_exists=if_exists,datadict=datadict)
        else:
            #krg['header']=False
            db_write(df,tb,dbtype="postgresql",conp=conp,if_exists='append')
        count+=1


# sql="select * from hefei.gg limit 100"
# conp=["postgres",'since2015','192.168.4.175','anhui','hefei']
# path="d:\\test.csv"

# def f1(df):
#     df['name']='xx'
#     return df 
# pg2csv(sql,conp,path)
# def f1(df):
#     df['name']='xx'
#     return df 

# conp1=["postgres",'since2015','192.168.4.175','anhui','hefei']

# conp2=["postgres",'since2015','192.168.4.175','mine','hunan']

# pg2pg("select * from hefei.gg limit 1000",'test',conp1,conp2,f=f1)
# path="D:/webroot/bstdata/base_20190421.csv"
# conp=["gpadmin","since2015",'192.168.4.179',"base_db","v2"]
# sql="select distinct on(html_key) * from v2.t_gg where ggstart_time>='2019-04-21' and ggstart_time<'2020-05-20' and html_key>7923769 "
# dfs=pg2csv(sql,conp,path,10,sep='\001')