
from lmf.dbv2 import db_command ,db_query
from lmf.bigdata import pg2csv
import sys 
import os 
from fabric import Connection
import time 
import traceback
from zlhawq.data import zhulong_diqu_dict
def est_t_gg_txt(conp):
    user,password,ip,db,schema=conp
    sql="""
    create table %s.t_gg_txt (
    html_key bigint,
    href text  not null  ,
    quyu text not null,

    txt text 

    )

    partition by list(quyu)
    (partition anhui_anqing values('anhui_anqing'),
    partition anhui_bengbu values('anhui_bengbu')
    )

    """%schema 
    db_command(sql,dbtype='postgresql',conp=conp)

#为 gg表新增\删除分区
def add_partition_t_gg_txt(quyu,conp):
    user,password,ip,db,schema=conp
    sql="alter table %s.t_gg_txt add partition %s values('%s')"%(schema,quyu,quyu)
    db_command(sql,dbtype='postgresql',conp=conp)

def drop_partition_t_gg_txt(quyu,conp):
    user,password,ip,db,schema=conp
    sql="alter table %s.t_gg_txt drop partition for('%s')"%(schema,quyu)
    db_command(sql,dbtype='postgresql',conp=conp)



def update_t_gg_txt(quyu,conp):

    user,password,ip,db,schema=conp

    sql="""
    insert into mine.t_gg_txt_1_prt_%s 


    select html_key ,href,quyu,mine.puretxt(page) as txt from v3.t_gg as b where quyu='%s'

    and not exists(select 1 from mine.t_gg_txt_1_prt_%s as a where a.html_key=b.html_key )

    
    """%(quyu,quyu,quyu)

    db_command(sql,dbtype='postgresql',conp=conp)



def add_quyu(quyu,conp_hawq):

    print("t_gg_txt表更新")
    user,password,ip,db,schema=conp_hawq
    print("1、准备创建分区-%s"%quyu)
    sql="""
    SELECT  partitionname
    FROM pg_partitions
    WHERE tablename='t_gg_txt' and schemaname='%s'
    """%(schema)
    df=db_query(sql,dbtype="postgresql",conp=conp_hawq)
    if quyu in df["partitionname"].values:
        print("%s-partition已经存在"%quyu)

    else:
        print('%s-partition还不存在'%quyu)
        add_partition_t_gg_txt(quyu,conp_hawq)
    print("2、准备更新t_gg_txt表--%s"%quyu)
    update_t_gg_txt(quyu,conp_hawq)


def restart_quyu(quyu,conp_hawq):

    print("t_gg_txt表restart")
    user,password,ip,db,schema=conp_hawq
    print("1、准备restart分区-%s"%quyu)
    sql="""
    SELECT  partitionname
    FROM pg_partitions
    WHERE tablename='t_gg_txt' and schemaname='%s'
    """%(schema)
    df=db_query(sql,dbtype="postgresql",conp=conp_hawq)
    if quyu in df["partitionname"].values:
        print("%s-partition已经存在"%quyu)
        drop_partition_t_gg_txt(quyu,conp_hawq)

    else:
        print('%s-partition还不存在'%quyu)
    add_partition_t_gg_txt(quyu,conp_hawq)
    print("2、准备更新t_gg_txt表--%s"%quyu)
    update_t_gg_txt(quyu,conp_hawq)

def add_quyus_sheng(sheng):
    quyus=zhulong_diqu_dict[sheng]
    bg=time.time()
    conp=["gpadmin","since2015","192.168.4.179","base_db","mine"]
    for quyu in quyus:
        try:
            add_quyu(quyu,conp)

            ed=time.time()
            cost=int(ed-bg)
            print("耗时--%d秒"%cost)
        except:
            traceback.print_exc()
        finally:
            bg=time.time()

def add_quyus_all():
    for sheng in zhulong_diqu_dict.keys():
        add_quyus_sheng(sheng)


#conp=["gpadmin","since2015","192.168.4.179","base_db","mine"]
#add_quyus_all()


