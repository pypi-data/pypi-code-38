from lmf.dbv2 import db_command ,db_query,db_query
from lmf.bigdata import pg2csv
import sys 
import os 
from fabric import Connection
import traceback
def est_tmp(txt):
    #quyu="anhui_bozhou"
    conp=['gpadmin','since2015','192.168.4.179','base_db','cdc']
    sql="""
    select tablename from pg_tables where schemaname='cdc'
    """
    df=db_query(sql,dbtype="postgresql",conp=conp)
    ex_tb='tmp'
    if ex_tb in df["tablename"].values:
        print("外部表tmp已经存在")
        sql="drop external table cdc.tmp;"
        db_command(sql,dbtype="postgresql",conp=conp)


        
    addr="192.168.4.187:8111"
    sql="""create  external table cdc.tmp (%s ) 
    location('gpfdist://192.168.4.187:8111/tmp.csv') format 'csv' (delimiter '\001' header quote '\002') log errors into errs segment reject limit 1000;  
    """%txt

    db_command(sql,dbtype="postgresql",conp=conp)


def pg2tmp(tbname):
    dir="/data/lmf"
    path1=os.path.join(dir,"tmp.csv")
    sql="select * from %s"%tbname
    print(sql)
    conp_pg=["postgres",'since2015','192.168.4.188','bid','public']
    pg2csv(sql,conp_pg,path1,chunksize=5000,sep='\001',quotechar='\002')


def est_local(tbname,txt):
    est_tmp(txt)
    pg2tmp(tbname)

def est_remote(tbname,txt):
    conp_remote=["root@192.168.4.187","rootHDPHAWQDatanode5@zhulong"]
    c=Connection(conp_remote[0],connect_kwargs={"password":conp_remote[1]})
    try:
        c.run("""/opt/python35/bin/python3 -c "from zlhawq.util import est_local;est_local('%s','%s') " """%(tbname,txt),pty=True,encoding='utf8')
    except:
        traceback.print_exc()
    finally:
        c.close()