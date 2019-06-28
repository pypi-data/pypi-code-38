from lmf.dbv2 import db_query ,db_command ,db_write 
from lmf.bigdata import pg2pg
from datetime import datetime,timedelta
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
import time 
#在目标conp创建bd表
def est_bd():
    conp=["gpadmin","since2015",'192.168.4.179','base_db','bid']
    user,passwd,host,db,schema=conp
    sql="""
    create table %s.bd (
    bd_key  serial  ,
    bd_name text  not null ,
    bd_bh  text ,
    zhaobiaoren text ,

    zbdl text ,

    kzj  numeric(30,4),

    xm_name text,
    fabu_time timestamp(0),
    quyu text not null 

    )
    """%(schema)
    db_command(sql,dbtype="postgresql",conp=conp)





#在用conp所在数据库更新,默认bd_update的表一定要在cdc 
def bd_update(quyu):
    conp=["gpadmin","since2015",'192.168.4.179','base_db','bid']
    user,passwd,host,db,schema=conp
    sql="""
    insert into bid.bd(bd_name,bd_bh,zhaobiaoren,zbdl,kzj,fabu_time,quyu)

    select bd_name,bd_bh,zhaobiaoren,zbdl,kzj,fabu_time,quyu from(
    SELECT
    distinct on(bd_guid)
     m1.get_js_v(info,'bd_guid')  as bd_guid

    ,m1.get_js_v(info,'bd_name')  as bd_name

    ,m1.get_js_v(info,'bd_bh')  as bd_bh


    ,m1.get_js_v(info,'zbr')  as zhaobiaoren


    ,m1.get_js_v(info,'zbdl')  as zbdl

    ,m1.get_js_v(info,'kzj')::float  as kzj

    ,fabu_time 
    ,quyu 
      FROM v3.t_gg where quyu='%s' and  m1.get_js_v(info,'bd_name') is not null

    order by m1.get_js_v(info,'bd_guid') ,fabu_time asc 
    ) as t 

    where not exists(select bd_name from bid.bd as a where a.bd_name=t.bd_name)
    """%(quyu)
    db_command(sql,dbtype="postgresql",conp=conp)