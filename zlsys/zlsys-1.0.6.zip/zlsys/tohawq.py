
from lmf.dbv2 import db_command ,db_query
from lmf.bigdata import pg2csv
import sys 
import os 
from fabric import Connection

import traceback
#为 gg表新增\删除分区
def est_zlsys(quyu,conp):
    user,password,ip,db,schema=conp
    sql="""
        CREATE TABLE .t_gg_zlsys_yunnan_kunming (
        bd_guid text,
        gg_name text ,
        gg_href text ,
        fabu_time timestamp,
        ggtype text ,
        quyu text ,
        diqu text ,
        create_time timestamp,
        info text ,
        page text 
        )

    """
    db_command(sql,dbtype='postgresql',conp=conp)

def drop_zlsys(quyu,conp):
    user,password,ip,db,schema=conp
    sql="alter table %s.gg drop partition for('%s')"%(schema,quyu)
    db_command(sql,dbtype='postgresql',conp=conp)




def est_cdc_t_gg(quyu,addr,conp):
    #quyu="anhui_bozhou"
    arr=quyu.split("_")
    s1,s2=arr[0],'_'.join(arr[1:])
    #addr="192.168.4.187:8111"
    #conp=['gpadmin','since2015','192.168.4.179','base_db','cdc']
    sql="""create  external table cdc.t_gg_%s (bd_guid text,gg_name text ,gg_href  text ,fabu_time timestamp ,ggtype text ,quyu text , diqu text ,create_time timestamp ,info text,page text ) 
    location('gpfdist://%s/t_gg_cdc_%s.csv') format 'csv' (delimiter '\001' header quote '\002') log errors into errs segment reject limit 1000;  
    """%(quyu,addr,quyu)

    db_command(sql,dbtype="postgresql",conp=conp)





#将pg数据导入到文件系统下的csv

def out_t_gg_all(quyu,dir,conp):
    path1=os.path.join(dir,"t_gg_cdc_%s.csv"%quyu)
    print(path1)
    arr=quyu.split("_")
    s1,s2=arr[0],'_'.join(arr[1:])
    sql="""select * from %s.t_gg  """%(s2)
    #df=db_query(sql=sql,dbtype="postgresql",conp=conp)

    #df.to_csv(path1,sep='\001',quotechar='\002',index=False)
    pg2csv(sql,conp,path1,chunksize=10000,sep='\001',quotechar='\002')


def add_quyu():
    quyu="zlsys_yunnan_kunming"
    conp1=["postgres","since2015","192.168.4.175","zlsys","yunnan_kunming"]
    conp2=["gpadmin","since2015","192.168.4.179","base_db","zlsys"]
    dir='/data/lmf'
    addr='192.168.4.187:8111'
    out_t_gg_all(quyu,dir,conp1)
    est_cdc_t_gg(quyu,addr,conp2)

add_quyu()





