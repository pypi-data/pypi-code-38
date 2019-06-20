from lmf.dbv2 import db_query ,db_command ,db_write 
from lmf.bigdata import pg2pg
from datetime import datetime,timedelta
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
import time
from lmf.bigdata import pg2pg 

def m1tosrc():
    conp_pg1=['postgres','since2015','192.168.4.188','base','m1']
    conp_pg2=['postgres','since2015','192.168.4.188','bid','src']

    tbs=db_query("select tablename from pg_tables where schemaname='m1' ",dbtype="postgresql",conp=conp_pg1)['tablename'].values.tolist()

    for tb in tbs[1:]:
        sql="select * from m1.%s"%tb 
        datadict={"gg_fabutime":TIMESTAMP(),"kzj":NUMERIC(),"zhongbiaojia":NUMERIC(),"html_key":BIGINT()}
        pg2pg(sql,tb,conp_pg1,conp_pg2,chunksize=10000,datadict=datadict)


conp_pg1=['postgres','since2015','192.168.4.188','base','public']
conp_pg2=['postgres','since2015','192.168.4.188','bid','src']

tbs=['gg_zhongbiao','zhongbiao']
for tb in tbs:
    sql="select * from public.%s"%tb 
    datadict={"gg_fabutime":TIMESTAMP(),"zhongbiaojia":NUMERIC(),"html_key":BIGINT()}
    pg2pg(sql,tb,conp_pg1,conp_pg2,chunksize=10000,datadict=datadict)