from common import * 
from lmf.dbv2 import db_command ,db_query 
from datetime import datetime ,timedelta

import traceback
def alter_column(conp,tbname):
    user,passwd,host,db,schema=conp

    arr=["bm_endtime","tb_endtime","bzj_time","kb_time","pb_time","db_time"]
    for w in arr:
        print("修改 %s 为timestamp类型"%w)
        sql="""alter table "%s"."%s" alter column %s type timestamp(0)  using to_timestamp( (%s::bigint)/1000)"""%(schema,tbname,w,w)
        db_command(sql,dbtype="postgresql",conp=conp)

    brr=["kzj","zhongbiaojia"]

    for w in brr:
        print("修改 %s 为numeric(30,4)类型"%(w))

        sql="""alter table "%s"."%s" alter column %s type numeric(30,4)  using %s::numeric(30,4) """%(schema,tbname,w,w)
        db_command(sql,dbtype="postgresql",conp=conp)
    crr=["gg_fabutime"]
    for w in crr:
        print("修改 %s 为timestamp类型"%(w))

        sql="""alter table "%s"."%s" alter column %s type timestamp(0) using %s::timestamp(0)  """%(schema,tbname,w,w)
        db_command(sql,dbtype="postgresql",conp=conp)


def kunming_base(path,conp,tbname,jytype):
    #path="D:/bsttmp/昆明工程建设存量"
    user,passwd,host,db,schema=conp
    #conp=["postgres","since2015","192.168.4.188","bid","zlsys"]

    #tbname="gg"
    gg_tbname="base_%s_tmp1"%jytype
    html_tbname="base_%s_tmp2"%jytype
    write_gg(path,conp,gg_tbname,jytype)
    write_html(path,conp,tbname=html_tbname)

    sql="""select a.*,b.page into %s.%s from %s.%s as a , %s.%s as b  where  a.gg_file=b.guid """%(schema,tbname,schema,gg_tbname,schema,html_tbname)
    db_command(sql,dbtype="postgresql",conp=conp)
    sql="drop table if exists %s.%s;drop table if exists %s.%s;"%(schema,gg_tbname,schema,html_tbname)
    db_command(sql,dbtype="postgresql",conp=conp)

    alter_column(conp,tbname)



def task_kunming_base(conp):
    user,passwd,host,db,schema=conp
    path="D:/bsttmp/昆明工程建设存量"

    

    kunming_base(path,conp,tbname="t_gg_gcjs",jytype="gcjs")

    path="D:/bsttmp/昆明政府采购存量"


    kunming_base(path,conp,tbname="t_gg_zfcg",jytype="zfcg")

    sql="""with a as (select * from %s.t_gg_gcjs union all select * from %s.t_gg_zfcg )
    select * into %s.t_gg_src from a 
    """%(schema,schema,schema)
    db_command(sql,dbtype="postgresql",conp=conp)

    sql="drop table if exists %s.t_gg_gcjs;drop table if exists %s.t_gg_zfcg;"%(schema,schema)
    db_command(sql,dbtype="postgresql",conp=conp)






def task_kunming_cdc(conp,date):
    user,passwd,host,db,schema=conp
    update("昆明市","gcjs",date,conp)
    update("昆明市","zfcg",date,conp)
    print("增量下载到数据库")
    tbs=db_query("""select tablename from pg_tables where schemaname='%s' and tablename ~'gg_cdc|html_cdc' order by tablename """%schema
        ,dbtype="postgresql",conp=conp)['tablename'].values.tolist()
    print(tbs)
    n=int(len(tbs)/2)
    for i in range(n):
        j=i+1
        tbname='t_gg_src_%d_cdc'%j
        gg_tbname,html_tbname=tbs[2*i],tbs[2*i+1]
        sql="""drop table if exists %s.%s ;
        select a.*,b.page into %s.%s from %s.%s as a , %s.%s as b  where  a.gg_file=b.guid """%(schema,tbname,schema,tbname,schema,gg_tbname,schema,html_tbname)
        db_command(sql,dbtype="postgresql",conp=conp)
        sql="drop table if exists %s.%s;drop table if exists %s.%s;"%(schema,gg_tbname,schema,html_tbname)
        db_command(sql,dbtype="postgresql",conp=conp)
        alter_column(conp,tbname)



def cdc_to_src(conp):
    user,passwd,host,db,schema=conp
    tbs=db_query("""select tablename from pg_tables where schemaname='%s' and tablename ~'t_gg.*cdc' order by tablename """%schema
        ,dbtype="postgresql",conp=conp)['tablename'].values.tolist()
    for tbname in tbs:
        print("更新-%s表"%tbname)
        sql="""insert into %s.t_gg_src 
            select * from %s.%s as a where not exists( select 1 from %s.t_gg_src as b  where a.gg_file=b.gg_file )
            """%(schema,schema,tbname,schema)
        print(sql)
        db_command(sql,dbtype="postgresql",conp=conp)



def task_kunming_update(conp,date):
    task_kunming_cdc(conp,date)
    cdc_to_src(conp)

def base_from_dates(conp,bdate):
    nowdate=datetime.strftime(datetime.now(),'%Y-%m-%d')
    while bdate!=nowdate:
        try:
            print(bdate)
            task_kunming_update(conp,bdate)
        except:
            traceback.print_exc()
        finally:
            bdate=datetime.strftime(datetime.strptime(bdate,'%Y-%m-%d')+timedelta(days=1),'%Y-%m-%d')



###########################################接口应用层

#一、先恢复base部分
#task_kunming_base
#二、从某日开始补齐
#base_from_dates(conp,'2019-05-01')
#每天的更新从昨天开始

conp=["postgres","since2015","192.168.4.175","zlsys","yunnan_kunming"]
nowdate=datetime.strftime(datetime.now(),'%Y-%m-%d')
yestoday=datetime.strftime(datetime.strptime(nowdate,'%Y-%m-%d')-timedelta(days=1),'%Y-%m-%d')
#base_from_dates(conp,yestoday)