
from lmf.dbv2 import db_command ,db_query
from lmf.bigdata import pg2csv
import sys 
import os 
from fabric import Connection

from zlhawq.core import add_partition_t_gg,drop_partition_t_gg,update_t_gg,est_cdc_t_gg,est_funs

#from zlhawq.core import



##############################这一部分更新从特定表录入的信息 zlsys部分


def out_t_gg_ftb(quyu,dir,conp,tb='t_gg'):
    path1=os.path.join(dir,"t_gg_cdc_%s.csv"%quyu)
    print(path1)
    arr=quyu.split("_")
    s1,s2=arr[0],'_'.join(arr[1:])
    sql="""select guid,gg_name,fabu_time,href,ggtype,jytype,diqu,quyu,info,page from %s.%s where fabu_time is not null
        """%(s2,tb)
    print(sql)
    #df=db_query(sql=sql,dbtype="postgresql",conp=conp)

    #df.to_csv(path1,sep='\001',quotechar='\002',index=False)
    pg2csv(sql,conp,path1,chunksize=10000,sep='\001',quotechar='\002')




def add_quyu_tmp(quyu,conp_pg,conp_hawq,dir,addr,tag='all'):
    print("t_gg表更新")
    user,password,ip,db,schema=conp_hawq
    print("1、准备创建分区")
    sql="""
    SELECT  partitionname
    FROM pg_partitions
    WHERE tablename='t_gg' and schemaname='%s'
    """%(schema)
    df=db_query(sql,dbtype="postgresql",conp=conp_hawq)
    if quyu in df["partitionname"].values:
        print("%s-partition已经存在"%quyu)

    else:
        print('%s-partition还不存在'%quyu)
        add_partition_t_gg(quyu,conp_hawq)

    print("2、准备创建外部表")

    sql="""
    select tablename from pg_tables where schemaname='cdc'
    """
    df=db_query(sql,dbtype="postgresql",conp=conp_hawq)
    ex_tb='t_gg_cdc_%s'%quyu
    if ex_tb in df["tablename"].values:
        print("外部表%s已经存在"%quyu)
 
    else:
        print('外部表%s还不存在'%quyu)
        est_cdc_t_gg(quyu,addr,conp_hawq)

    print("3、准备从RDBMS导出csv")
    print("创建函数")
    est_funs(conp_pg)
    if tag=='all':
        out_t_gg_ftb(quyu,dir,conp_pg)
    # else:
    #     out_t_gg_cdc(quyu,dir,conp_pg)

    print("4、hawq中执行更新、插入语句")

    update_t_gg(quyu,conp_hawq)


def add_quyu(quyu,tag='all'):
    arr=quyu.split("_")
    s1,s2=arr[0],'_'.join(arr[1:])

    conp_pg=["postgres","since2015","192.168.4.175",s1,s2]
    conp_hawq=["gpadmin","since2015","192.168.4.179","base_db","v3"]
    dir='/data/lmf'
    addr='192.168.4.187:8111'
    add_quyu_tmp(quyu,conp_pg,conp_hawq,dir,addr,tag=tag)
