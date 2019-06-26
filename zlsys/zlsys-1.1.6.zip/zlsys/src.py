from download import * 
from lmf.dbv2 import db_command ,db_query 
from datetime import datetime ,timedelta

import traceback

#此模块负责数据导入到t_gg_src

def src_cdc1(shi,jytype,conp,date):
    user,passwd,host,db,schema=conp
    update(shi,jytype,date,conp)

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
        #alter_column(conp,tbname)

def src_cdc2(conp):
    user,passwd,host,db,schema=conp
    tbs=db_query("""select tablename from pg_tables where schemaname='%s' and tablename ~'t_gg.*cdc' order by tablename """%schema
        ,dbtype="postgresql",conp=conp)['tablename'].values.tolist()
    tbs1=db_query("""select tablename from pg_tables where schemaname='%s'  order by tablename """%schema
        ,dbtype="postgresql",conp=conp)['tablename'].values.tolist()
    for tbname in tbs:
        print("更新,-%s表插入到t_gg_src"%tbname)
        print(tbs1)
        if 't_gg_src' not in tbs1:
            sql="""
                select distinct on(gg_file) * into %s.t_gg_src from %s.%s 
                """%(schema,schema,tbname)
        else:

            sql="""insert into %s.t_gg_src 
                select * from %s.%s as a where not exists( select 1 from %s.t_gg_src as b  where a.gg_file=b.gg_file )
                """%(schema,schema,tbname,schema)
        print(sql)
        db_command(sql,dbtype="postgresql",conp=conp)


def src_update(shi,jytype,conp,date):
    src_cdc1(shi,jytype,conp,date)
    src_cdc2(conp)

def src_update_dates(shi,jytype,conp,bdate):
    nowdate=datetime.strftime(datetime.now(),'%Y-%m-%d')
    while bdate!=nowdate:
        try:
            print(bdate)
            src_update(shi,jytype,conp,bdate)
        except:
            traceback.print_exc()
        finally:
            bdate=datetime.strftime(datetime.strptime(bdate,'%Y-%m-%d')+timedelta(days=1),'%Y-%m-%d')
    try:
        print(bdate)
        src_update(shi,jytype,conp,bdate)
    except:
        traceback.print_exc()




#src_update_dates('保山市','gcjs',['postgres','since2015','192.168.4.175','zlsys','yunnan_baoshan'],'2019-06-13')
# src_update_dates('遂宁市','zfcg',['postgres','since2015','192.168.4.175','zlsys','sichuan_suining'],'2019-06-13')
#src_update_dates('曲靖市','zfcg',['postgres','since2015','192.168.4.175','zlsys','yunnan_qujingshi'],'2019-06-22')

