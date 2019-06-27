import hashlib
from lmf.dbv2 import db_command ,db_query

import os 
import pandas as pd 

def cut(a,b):
    i=5
    tmp=a[:i]
    while tmp!=a:
        if not b.startswith(tmp):
            break
        i+=1
        tmp=a[:i]
    if not max(i/len(a),i/len(b))>0.6:return None
    if tmp==a and b.startswith(tmp):target=tmp 
    else:
        target=tmp[:-1]
    return target


def count_str(word,trr):
    k=0 
    for w in trr:
        if word in w:k+=1
    return k 
def get_bdname(word,arr,hx=None):
    if hx is not None:
        for w in hx:
            if w in word :return w
    target=word
    j=1
    ptmp=None
    trr=arr[ max(arr[arr==word].index[0]-10,0) :arr[arr==word].index[0]+10]

    data=[]
    for w in trr :

        tmp=cut(target,w)
        if  tmp is  None:continue

        k=count_str(tmp,trr)

        if k!=1 and k<=5 and tmp!=word:data.append((tmp,k))


    data.sort(key=lambda x:x[1])
    if data==[]:return None 
    target=data[0][0]
    return target

def get_bdlist(arr,cdc=None,hx=None):
    data=[]
    if cdc is not None:trr=cdc 
    else:trr=arr
    for w in trr:
        target=get_bdname(w,arr,hx)
        if target is not None:data.append(target)
    data=list(set(data))
    return data

######上面是算法



def md5hex(s):
    m=hashlib.md5(s.encode())

    x1=m.hexdigest()
    return x1 


def est_func():
    conp=['gpadmin','since2015','192.168.4.179','base_db','bid']
    sql="""
create or replace function  bid.md5hex(name_quyu text) returns text 

as $$

import hashlib 
if name_quyu is None:return None
m=hashlib.md5(name_quyu.encode())

x1=m.hexdigest()
return x1 



$$ language plpython3;
    """
    conp=['gpadmin','since2015','192.168.4.179','base_db','bid']

    db_command(sql,dbtype="postgresql",conp=conp)


def est_t_bd():
    conp=['gpadmin','since2015','192.168.4.179','base_db','bid']
    user,password,ip,db,schema=conp
    sql="""
    create table %s.t_bd (
    bd_key  serial,
    bd_guid text not null ,
    bd_name text not null ,
    quyu text  not null )

    partition by list(quyu)
    (partition anhui_anqing values('anhui_anqing'),
    partition anhui_bengbu values('anhui_bengbu')
    )

    """%schema 
    db_command(sql,dbtype='postgresql',conp=conp)

#为 gg表新增\删除分区
def add_partition_t_bd(quyu):
    conp=['gpadmin','since2015','192.168.4.179','base_db','bid']
    user,password,ip,db,schema=conp
    sql="alter table %s.t_bd add partition %s values('%s')"%(schema,quyu,quyu)
    db_command(sql,dbtype='postgresql',conp=conp)

def drop_partition_t_bd(quyu):
    conp=['gpadmin','since2015','192.168.4.179','base_db','bid']
    user,password,ip,db,schema=conp
    sql="alter table %s.t_bd drop partition for('%s')"%(schema,quyu)
    db_command(sql,dbtype='postgresql',conp=conp)

def est_cdc_t_bd(quyu):
    #quyu="anhui_bozhou"
    conp=['gpadmin','since2015','192.168.4.179','base_db','cdc']
    arr=quyu.split("_")
    s1,s2=arr[0],'_'.join(arr[1:])
    addr="192.168.4.187:8111"
    #conp=['gpadmin','since2015','192.168.4.179','base_db','cdc']
    sql="""create  external table cdc.t_bd_cdc_%s (bd_guid text,bd_name text,quyu text ) 
    location('gpfdist://%s/t_bd_cdc_%s.csv') format 'csv' (delimiter '\001' header quote '\002') log errors into errs segment reject limit 1000;  
    """%(quyu,addr,quyu)

    db_command(sql,dbtype="postgresql",conp=conp)

####爬虫的标段
def out_t_bd_pc_all(quyu):
    path1=os.path.join('/data/lmf',"t_bd_cdc_%s.csv"%quyu)
    print(path1)
    conp=['gpadmin','since2015','192.168.4.179','base_db','bid']


    sql="select gg_name from v3.t_gg_1_prt_%s order by gg_name"%quyu

    df=db_query(sql,dbtype="postgresql",conp=conp)

    arr=df['gg_name']
    data=get_bdlist(arr)
    df=pd.DataFrame({"bd_name":data})
    df['quyu']=quyu 
    df['bd_guid']=df['bd_name'].map(lambda x:md5hex(x+quyu))
    df=df[['bd_guid','bd_name','quyu']]
    print("输出df到 csv")
    df.to_csv(path1,index=False,chunksize=5000,sep='\001',quotechar='\002') 

def out_t_bd_pc_cdc(quyu):
    path1=os.path.join('/data/lmf',"t_bd_cdc_%s.csv"%quyu)
    print(path1)
    conp=['gpadmin','since2015','192.168.4.179','base_db','bid']


    sql="select gg_name from v3.t_gg_1_prt_%s order by gg_name"%quyu

    df=db_query(sql,dbtype="postgresql",conp=conp)

    arr=df['gg_name']
    #cdc=
    sql="select gg_name from v3.t_gg_1_prt_%s order by html_key desc limit 1000"%quyu

    df=db_query(sql,dbtype="postgresql",conp=conp)

    cdc=df['gg_name']
    #hx
    sql="select bd_name from bid.t_bd_1_prt_%s "%quyu

    df=db_query(sql,dbtype="postgresql",conp=conp)

    hx=set(df['bd_name'].values)

    data=get_bdlist(arr,cdc,hx)
    df=pd.DataFrame({"bd_name":data})
    df['quyu']=quyu 
    df['bd_guid']=df['bd_name'].map(lambda x:md5hex(x+quyu))
    df=df[['bd_guid','bd_name','quyu']]

    print("输出df到 csv")
    df.to_csv(path1,index=False,chunksize=5000,sep='\001',quotechar='\002') 



def update_t_bd_pc(quyu):
    conp=['gpadmin','since2015','192.168.4.179','base_db','bid']
    user,password,ip,db,schema=conp

    sql="""
    insert into %s.t_bd_1_prt_%s(bd_guid,bd_name,quyu)
    SELECT 
    distinct on(bd_guid)
    bd_guid,bd_name,quyu

     FROM cdc.t_bd_cdc_%s a where   not exists (select 1 from %s.t_bd_1_prt_%s as b where   a.bd_guid=b.bd_guid)  
    
    """%(schema,quyu,quyu,schema,quyu)

    db_command(sql,dbtype='postgresql',conp=conp)


def add_quyu_tmp_pc(quyu,tag='all'):
    conp_hawq=['gpadmin','since2015','192.168.4.179','base_db','bid']
    print("t_bd表更新")
    user,password,ip,db,schema=conp_hawq
    print("1、准备创建分区")
    sql="""
    SELECT  partitionname
    FROM pg_partitions
    WHERE tablename='t_bd' and schemaname='%s'
    """%(schema)
    df=db_query(sql,dbtype="postgresql",conp=conp_hawq)
    if quyu in df["partitionname"].values:
        print("%s-partition已经存在"%quyu)

    else:
        print('%s-partition还不存在'%quyu)
        add_partition_t_bd(quyu)

    print("2、准备创建外部表")

    sql="""
    select tablename from pg_tables where schemaname='cdc'
    """
    df=db_query(sql,dbtype="postgresql",conp=conp_hawq)
    ex_tb='t_bd_cdc_%s'%quyu
    if ex_tb in df["tablename"].values:
        print("外部表%s已经存在"%quyu)

    else:
        print('外部表%s还不存在'%quyu)
        est_cdc_t_bd(quyu)

    print("3、准备从RDBMS导出csv")
    if tag=='all':

        out_t_bd_pc_all(quyu)
    else:
        out_t_bd_pc_cdc(quyu)


    print("4、hawq中执行更新、插入语句")

    update_t_bd_pc(quyu)

def restart_quyu_tmp_pc(quyu):
    conp_hawq=['gpadmin','since2015','192.168.4.179','base_db','bid']
    print("t_bd 一个区域rebuild")
    user,password,ip,db,schema=conp_hawq
    print("1、准备删除分区")
    sql="""
    SELECT  partitionname
    FROM pg_partitions
    WHERE tablename='t_bd' and schemaname='%s'
    """%(schema)
    df=db_query(sql,dbtype="postgresql",conp=conp_hawq)
    if quyu in df["partitionname"].values:
        print("%s-partition已经存在,删之"%quyu)
        drop_partition_t_bd(quyu)

    else:
        print('%s-partition还不存在'%quyu)

    add_quyu_tmp_pc(quyu,'all')


#######