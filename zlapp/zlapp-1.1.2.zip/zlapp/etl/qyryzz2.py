from lmf.bigdata import pg2csv 
from lmf.dbv2 import db_command,db_query
from fabric import Connection
import traceback
import os 
from sqlalchemy.dialects.postgresql import TEXT,ARRAY
def est_external_table():
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    sql="""create  external table cdc.jz_jianzhu_ryxx_html (href text,page text,name text, zjhm text,gender text,zj_type text ) 
    location('gpfdist://192.168.4.187:8111/jz_jianzhu_ryxx_html.csv') format 'csv' (delimiter '\001' header quote '\002') log errors into errs segment reject limit 1000;  
    """
    db_command(sql,dbtype="postgresql",conp=conp)

def out_csv():
    path1=os.path.join("/data/lmf","jz_jianzhu_ryxx_html.csv")
    conp_src=["postgres","since2015","192.168.4.188",'bid','jianzhu']
    sql="""select ryxx_href as href,replace(replace(replace(replace(zyzcxx,'\001',''),'\002',''),'\r',''),'\n','') as page 
    ,ryxx_name  as name ,sex as gender,id_number as zjhm , id_type as zj_type 
    from jianzhu.jianzhu_ryxx_html """
    print(sql)
    pg2csv(sql,conp_src,path1,chunksize=5000,sep='\001',quotechar='\002')

def est_table_local():
    conp_hawq=["gpadmin","since2015","192.168.4.179","base_db","public"]
    print("1、准备创建外部表")

    sql="""
    select tablename from pg_tables where schemaname='cdc'
    """
    df=db_query(sql,dbtype="postgresql",conp=conp_hawq)
    ex_tb='jz_jianzhu_ryxx_html'
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
        c.run("""/opt/python35/bin/python3 -c "from zlapp.etl.qyryzz2 import est_table_local;est_table_local() " """,pty=True,encoding='utf8')
    except:
        traceback.print_exc()
    finally:
        c.close()