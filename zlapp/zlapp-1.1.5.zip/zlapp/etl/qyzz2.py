from lmf.bigdata import pg2csv ,pg2pg
from lmf.dbv2 import db_command,db_query
from fabric import Connection
import traceback
import os 
from sqlalchemy.dialects.postgresql import TEXT,ARRAY
def est_external_table():
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    sql="""create  external table cdc.jz_gg_html (href text,page text ) 
    location('gpfdist://192.168.4.187:8111/jz_gg_html.csv') format 'csv' (delimiter '\001' header quote '\002') log errors into errs segment reject limit 1000;  
    """
    db_command(sql,dbtype="postgresql",conp=conp)

def out_csv():
    path1=os.path.join("/data/lmf","jz_gg_html.csv")
    conp_src=["postgres","since2015","192.168.4.188",'bid','jianzhu']
    sql="""select href,replace(replace(replace(replace(page,'\001',''),'\002',''),'\r',''),'\n','') as page from jianzhu.gg_html """
    print(sql)
    pg2csv(sql,conp_src,path1,chunksize=5000,sep='\001',quotechar='\002')

def est_table_local():
    conp_hawq=["gpadmin","since2015","192.168.4.179","base_db","public"]
    print("1、准备创建外部表")

    sql="""
    select tablename from pg_tables where schemaname='cdc'
    """
    df=db_query(sql,dbtype="postgresql",conp=conp_hawq)
    ex_tb='jz_gg_html'
    if ex_tb in df["tablename"].values:
        print("外部表已经存在")

    else:
        print('外部表还不存在')
        est_external_table()

    print("2、导出数据到csv")
    out_csv()

def est_table_remote():
    conp_remote=["root@192.168.4.187","rootHDPHAWQDatanode5@zhulong"]
    c=Connection(conp_remote[0],connect_kwargs={"password":conp_remote[1]})
    try:
        c.run("""/opt/python35/bin/python3 -c "from zlapp.etl.qyzz2 import est_table_local;est_table_local() " """,pty=True,encoding='utf8')
    except:
        traceback.print_exc()
    finally:
        c.close()



###入库hawq后的操作,解析

#外部表写入到内部表
def ptb1():

    sql="""
       
    drop table if exists jianzhu.gg_html;

    SELECT * into jianzhu.gg_html  FROM "cdc"."jz_gg_html";
        """
    conp_hawq=["gpadmin","since2015","192.168.4.179","base_db","public"]

    db_command(sql,dbtype="postgresql",conp=conp_hawq)


#解析page
def ptb2():
    sql="""
     drop table if exists jianzhu.gg_html_result;
    select href,jianzhu.qyzzext(page) as pageresult into jianzhu.gg_html_result  from jianzhu.gg_html
    """
    conp_hawq=["gpadmin","since2015","192.168.4.179","base_db","public"]

    db_command(sql,dbtype="postgresql",conp=conp_hawq)

#生成原始表
def ptb3():
    sql="""
    drop table if exists jianzhu.qyzz;
    SELECT href
    ,json_kv(unnest(pageresult),'zzbh') as zzbh
    ,json_kv(unnest(pageresult),'gsd') as gsd
    ,json_kv(unnest(pageresult),'jglx') as jglx
    ,json_kv(unnest(pageresult),'zzmc') as zzmc
    ,json_kv(unnest(pageresult),'bgdate') as bgdate
    ,json_kv(unnest(pageresult),'eddate') as edddate
    ,json_kv(unnest(pageresult),'fbjg') as fbjg
    ,json_kv(unnest(pageresult),'tydm') as tydm
    ,json_kv(unnest(pageresult),'fddbr') as fddbr
    ,json_kv(unnest(pageresult),'zzlb') as zzlb
    ,json_kv(unnest(pageresult),'entname') as entname
    ,json_kv(unnest(pageresult),'jgdz') as jgdz
    ,json_kv(unnest(pageresult),'qita') as qita
    into jianzhu.qyzz 
     FROM "jianzhu"."gg_html_result"

    where pageresult is not null 
    """
    conp_hawq=["gpadmin","since2015","192.168.4.179","base_db","public"]

    db_command(sql,dbtype="postgresql",conp=conp_hawq)

#####hawq出库

def ptb4():
    conp_hawq=["gpadmin","since2015","192.168.4.179","base_db","public"]
    conp_pg=["postgres","since2015","192.168.4.188",'bid','cdc']
    sql="select * from jianzhu.qyzz"
    pg2pg(sql,'qyzz',conp_hawq,conp_pg,chunksize=10000)



def est_qyzz():
    est_table_remote()
    ptb1()
    ptb2()
    ptb3()
    ptb4()