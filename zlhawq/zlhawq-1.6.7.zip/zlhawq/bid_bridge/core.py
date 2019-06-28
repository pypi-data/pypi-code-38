
from lmf.dbv2 import db_command ,db_query
from lmf.bigdata import pg2csv
import sys 
import os 
from fabric import Connection

import traceback
def est_t_bd_gg():
    conp=["gpadmin","since2015","192.168.4.179","base_db","bid"]
    user,password,ip,db,schema=conp
    sql="""
    create table %s.t_bd_gg (
    html_key  bigint,
    bd_key bigint,
    quyu text not null)
    partition by list(quyu)
    (partition anhui_anqing values('anhui_anqing'),
    partition anhui_bengbu values('anhui_bengbu')
    )

    """%schema 
    db_command(sql,dbtype='postgresql',conp=conp)


#为 gg表新增\删除分区
def add_partition_t_bd_gg(quyu):
    conp=["gpadmin","since2015","192.168.4.179","base_db","bid"]
    user,password,ip,db,schema=conp
    sql="alter table %s.t_bd_gg add partition %s values('%s')"%(schema,quyu,quyu)
    db_command(sql,dbtype='postgresql',conp=conp)

def drop_partition_t_bd_gg(quyu):
    conp=["gpadmin","since2015","192.168.4.179","base_db","bid"]
    user,password,ip,db,schema=conp
    sql="alter table %s.t_bd_gg drop partition for('%s')"%(schema,quyu)
    db_command(sql,dbtype='postgresql',conp=conp)


def update_t_bd_gg(quyu):
    conp=["gpadmin","since2015","192.168.4.179","base_db","bid"]
    sql="""
insert into bid.t_bd_gg_1_prt_%s
with a as (select html_key, gg_name from v3.t_gg where quyu='%s')
,b as (select bd_name,bd_key,quyu from bid.t_bd where quyu='%s')
,c as (select * ,row_number() over(partition by gg_name order by length(bd_name) desc,html_key  ) as cn from a,b  where  position(b.bd_name in a.gg_name)=1)

select distinct on (html_key) html_key,bd_key,quyu from c where cn=1 and not exists(
select 1 from bid.t_bd_gg as t where quyu='%s' and t.html_key=c.html_key)


    """%(quyu,quyu,quyu,quyu)
    db_command(sql,dbtype='postgresql',conp=conp)


def add_quyu_tmp(quyu):
    conp_hawq=["gpadmin","since2015","192.168.4.179","base_db","bid"]
    print("t_bd_gg表更新")
    user,password,ip,db,schema=conp_hawq
    print("1、准备创建分区")
    sql="""
    SELECT  partitionname
    FROM pg_partitions
    WHERE tablename='t_bd_gg' and schemaname='%s'
    """%(schema)
    df=db_query(sql,dbtype="postgresql",conp=conp_hawq)
    if quyu in df["partitionname"].values:
        print("%s-partition已经存在"%quyu)

    else:
        print('%s-partition还不存在'%quyu)
        add_partition_t_bd_gg(quyu)



    print("4、hawq中执行更新、插入语句")

    update_t_bd_gg(quyu)


def restart_quyu_tmp(quyu):
    conp_hawq=["gpadmin","since2015","192.168.4.179","base_db","bid"]
    print("t_bd_gg表更新")
    user,password,ip,db,schema=conp_hawq
    print("1、准备创建分区")
    sql="""
    SELECT  partitionname
    FROM pg_partitions
    WHERE tablename='t_bd_gg' and schemaname='%s'
    """%(schema)
    df=db_query(sql,dbtype="postgresql",conp=conp_hawq)
    if quyu in df["partitionname"].values:
        print("%s-partition已经存在"%quyu)
        drop_partition_t_bd_gg(quyu)


    print('%s-partition还不存在'%quyu)
    add_partition_t_bd_gg(quyu)



    print("4、hawq中执行更新、插入语句")

    update_t_bd_gg(quyu)




