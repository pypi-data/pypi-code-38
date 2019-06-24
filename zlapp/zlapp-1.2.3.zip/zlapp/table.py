from lmf.dbv2 import db_query ,db_command ,db_write 
from lmf.bigdata import pg2pg
from datetime import datetime,timedelta
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
import time 
#在目标conp创建bd表
def est_bd(conp):
    user,passwd,host,db,schema=conp
    sql="""
    create table %s.bd (
    bd_key  serial primary key ,
    bd_name text  not null ,
    bd_bh  text not null,
    zhaobiaoren text ,

    zbdl text ,

    kzj  numeric(30,4),

    xm_name text,
    fabu_time timestamp(0),
    quyu text not null ,
    unique(bd_name,bd_bh) 
    )
    """%(schema)
    db_command(sql,dbtype="postgresql",conp=conp)


#在用conp所在数据库更新,默认bd_update的表一定要在cdc 
def bd_update(tbname,conp,quyu):
    user,passwd,host,db,schema=conp
    sql="""
    with a as (
    SELECT distinct on(bd_name,bd_bh)
    bd_name,bd_bh,gg_fabutime,zbr,kzj,zbdl

    , '%s' as  quyu
     FROM "cdc"."%s"
    where zbr is not null  and bd_name is not null 
    order by bd_name,bd_bh,gg_fabutime asc)

     insert into %s.bd(bd_name,bd_bh,fabu_time,zhaobiaoren,kzj,zbdl,quyu)
      select bd_name,bd_bh,gg_fabutime::timestamp(0) as fabu_time,zbr,kzj::numeric(30,4) as kzj,
    zbdl,quyu from a where not exists(select 1 from %s.bd as b where a.bd_name=b.bd_name and a.bd_bh=b.bd_bh)
    """%(quyu,tbname,schema,schema)
    db_command(sql,dbtype="postgresql",conp=conp)



###################################gg表相关##########################

#从hawq中取一个月数据至gg表中

#1、写近一个月数据到pg
def gg_update_tmptb(conp_hawq,conp_pg,tbname='t_gg_app'):

    bgdate=datetime.strftime(datetime.now()-timedelta(days=30),'%Y-%m-%d')

    eddate=datetime.strftime(datetime.now()+timedelta(days=365),'%Y-%m-%d')

    bg=time.time()
    sql="""select * from v3.t_gg where fabu_time>='%s'  and fabu_time<'%s' and quyu not in('zlsys_yunnan_kunming') 
    union all 
    select * from v3.t_gg where quyu in ('zlsys_yunnan_kunming') 
    """%(bgdate,eddate)

    datadict={"html_key":BIGINT(),'guid':TEXT(),"gg_name":TEXT(),"href":TEXT(),"fabu_time":TIMESTAMP(),"ggtype":TEXT(),
    "jytype":TEXT(),"diqu":TEXT(),"quyu":TEXT(),"info":TEXT(),"page":TEXT(),"create_time":TIMESTAMP()}
    pg2pg(sql,tbname,conp_hawq,conp_pg,chunksize=5000,datadict=datadict)
    ed=time.time()
    cost=int(ed-bg)
    print("耗时%s秒"%cost)

#2、insert into gg

def gg_update_insert(conp):
    user,passwd,host,db,schema=conp
    sql1="""
    create or replace function public.quyu2ts(quyu text) returns text 
    as 
    $$

    txt=quyu.split('_')

    txt=' '.join(txt)
    return txt 


    $$ language plpython3u; 

    create or replace function public.title2ts(name text) returns text 
    as 
    $$
    import jieba 

    arr=filter(lambda x:len(x)>1, jieba.lcut(name))

    result=' '.join(arr)

    return result 

    $$ language plpython3u; 


    """

    db_command(sql1,dbtype="postgresql",conp=conp)

    print('更新gg')
    print("先truncate gg表 再插入")
    bg=time.time()
    sql_tmp="""    truncate table %s.gg;"""%(schema)
    db_command(sql_tmp,dbtype="postgresql",conp=conp)
    sql2="""

    insert into %s.gg(
    html_key,guid, gg_name,   href,   fabu_time,   ggtype, jytype, diqu,   quyu    ,  create_time    
    ,ts_title,ts_quyu
    )

    select  distinct on(guid)
    html_key,guid, gg_name,   href,   fabu_time,   ggtype, jytype, diqu,   quyu    ,  create_time,

    title2ts(gg_name)::tsvector,quyu2ts(quyu)::tsvector

    from cdc.t_gg_app as a where not exists(select 1 from %s.gg as b where a.html_key=b.html_key )
    """%(schema,schema)
    db_command(sql2,dbtype="postgresql",conp=conp)

    ed=time.time()
    cost=int(ed-bg)
    print("耗时%s秒"%cost)

#gg表更新bd_key 
#创建bd_gg_bridge 表
#创建bd_key 更新函数
#gg表更新person 和price


def gg_update_bdkey(conp):
    user,passwd,host,db,schema=conp
    sql="update %s.gg set bd_key=%s.guid_to_bdkey(guid)"%(schema,schema)
    db_command(sql,dbtype="postgresql",conp=conp)

#创建gg表

def est_gg(conp):
    user,passwd,host,db,schema=conp
    sql="""
    drop table if exists %s.gg ;
    create table %s.gg (
    html_key bigint primary key ,
    guid text unique,
    gg_name  text ,
    href text ,
    fabu_time timestamp(0),
    ggtype text , 

    jytype text ,
    quyu text,
    diqu text ,
    create_time timestamp(0),

    person  text ,

    price numeric(30,4),

    bd_key bigint ,
    ts_title tsvector,
    ts_quyu tsvector
    )
    """%(schema,schema)
    db_command(sql,dbtype="postgresql",conp=conp)


def est_bd_gg_bridge(conp):
    user,passwd,host,db,schema=conp
    sql="""create table %s.bd_gg_bridge(
    html_key bigint  ,

    guid text primary key,
    bd_key bigint 
    )

    """%schema
    db_command(sql,dbtype="postgresql",conp=conp)

def update_bd_gg_bridge(conp,tbname):
    user,passwd,host,db,schema=conp
    sql="""
    with t1 as  (  SELECT a.gg_file,a.bd_bh,a.bd_name,b.bd_key  FROM "cdc"."%s" as a ,public.bd as b 

    where a.bd_bh=b.bd_bh and a.bd_name=b.bd_name)

    ,t3 as (select t2.guid,t1.bd_key,t2.html_key from t1,cdc.t_gg_app as t2  where t1.gg_file=t2.guid)
    insert into %s.bd_gg_bridge(guid,bd_key,html_key) select distinct on(guid) * from t3 where not exists(select 1 from %s.bd_gg_bridge as b1 where b1.guid=t3.guid)
    """%(tbname,schema,schema)
    db_command(sql,dbtype="postgresql",conp=conp)


def est_fun_guid_bdkey(conp):
    user,passwd,host,db,schema=conp
    sql="""
create extension if not exists plpython3u;
create or replace function %s.guid_to_bdkey(guid text) returns bigint as 

$$
from collections import defaultdict 
if 'guid_bdkey_dict' not in GD.keys():
    sql="select guid ,bd_key from %s.bd_gg_bridge "
    a=plpy.execute(sql)
    guid_bdkey=defaultdict(str)
    for w in a:
        guid_bdkey[w['guid']]=w['bd_key']
    GD['guid_bdkey_dict']=guid_bdkey

if guid is None:return None 
result=GD['guid_bdkey_dict'][guid]
if result=='':return None

else:return result

$$ language plpython3u;

    """%(schema,schema)
    db_command(sql,dbtype="postgresql",conp=conp)


def est_gghtml(conp):
    user,passwd,host,db,schema=conp
    sql="drop table if exists %s.gg_html "%schema 
    db_command(sql,dbtype="postgresql",conp=conp)

    sql="select html_key,guid,page into %s.gg_html from cdc.t_gg_app"%(schema)
    db_command(sql,dbtype="postgresql",conp=conp)



#######################################################bd_dt表


def est_bd_dt(conp):
    user,passwd,host,db,schema=conp
    sql="""
    create table  %s.bd_dt(
    html_key   bigint primary key  ,

    guid text ,
    bd_key  bigint ,

    gg_name text,

    ggtype text,
    fabu_time timestamp(0) ,
    gg_info text , 
    create_time timestamp(0)

    )

    """%schema
    db_command(sql,dbtype="postgresql",conp=conp)

def update_bd_dt(conp):
    user,passwd,host,db,schema=conp
    sql="""
    insert into %s.bd_dt( html_key,   guid,   bd_key,gg_name, ggtype, fabu_time,  gg_info,    create_time)

    select html_key ,guid,guid_to_bdkey(guid) as bd_key,gg_name,ggtype,fabu_time,info as gg_info ,create_time 

    from cdc.t_gg_app  as a where  guid_to_bdkey(guid) is not null and not exists(select 1 from 

    %s.bd_dt as b where  a.html_key=b.html_key

    )
    """%(schema,schema)
    db_command(sql,dbtype="postgresql",conp=conp)





###############################企业资质#################################################

def est_fun_zzname_to_zzcode(conp):
    user,passwd,host,db,schema=conp
    sql="""
    CREATE or replace function %s.zzname_to_zzcode(name text) returns text 

    as $$
    if 'zzcode_dict' not in GD.keys():
        zzcode_dict={}
        a=plpy.execute('select distinct on(name) * from cdc.dict_zz')
        for w in a:
            zzcode_dict[w['name']]=w['zzcode']
        GD['zzcode_dict']=zzcode_dict 

    if name in GD['zzcode_dict']:return GD['zzcode_dict'][name]
    else :return None
            


    $$ language plpython3u ;

    """%schema
    db_command(sql,dbtype="postgresql",conp=conp)





conp=["postgres","since2015",'192.168.4.188','bid',"public"]
# est_bd(conp)

#bd_update('kunming_gcjs_gg',conp,'zlsys_yunnan_kunming')

# conp_hawq=["gpadmin","since2015",'192.168.4.179','base_db',"v3"]
# conp_pg=["postgres","since2015",'192.168.4.188','bid',"cdc"]

# gg_update_tmptb(conp_hawq,conp_pg)

# conp_pg=["postgres","since2015",'192.168.4.188','base',"test"]

# gg_update_insert(conp_pg) 

#bd_update("t_gg_src_kunming",conp,'zlsys_yunnan_kunming')