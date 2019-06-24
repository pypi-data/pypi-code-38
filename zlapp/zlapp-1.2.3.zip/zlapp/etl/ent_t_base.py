from lmf.dbv2 import db_query ,db_command ,db_write 
from lmf.bigdata import pg2pg
from zlapp.ent.todb import add_t_base_src


#企业相关表 


#1 接口加入新的数据

#将ent表中查不到的entname-tag归-1
def flush_tag0():
   
    sql="""
    update ent.ent as a set tag=-1 where not exists (select jgmc from ent.t_base_src as b where a.entname=b.jgmc);
    """
    db_command(sql,dbtype="postgresql",conp=['postgres','since2015','192.168.4.188','bid','ent'])
#add_t_base_src
#将ent表中查到的entname-tag归1
def flush_tag1():
    sql="""
    update ent.ent as a set tag=1 where exists (select jgmc from ent.t_base_src as b where a.entname=b.jgmc);
    """
    db_command(sql,dbtype="postgresql",conp=['postgres','since2015','192.168.4.188','bid','ent'])





#src2est
def t_base_src2est():
    sql=r"""
    insert into ent.t_base_est(jgmc,tydm,zch,jgdm,entid,clrq,jgdz,fddbr,jyfw,jjhy,jglx,zczj,zczj_bz,zczj_sj,zczj_sj_bz,taxdm,fromtime,totime,djbumen,jyzt,engname,bondnum
    ,zggm,email,phone,website,staff_info,alias,diaoxiaodate,diaoxiaoreason,zhuxiaodate,zhuxiaoreason,logo)
    select 
    distinct on(jgmc)
     regexp_replace(src->>'name','[^\u4E00-\u9FA5a-z0-9A-Z\(\)（）]','','g') as jgmc
    ,src->>'creditCode' as tydm
    ,src->>'regNumber'  as zch
    ,src->>'orgNumber'  as jgdm 
    ,src->>'id'  as entid 
    ,to_timestamp((src->>'estiblishTime')::bigint/1000)::timestamp(6) as clrq
    ,src->>'regLocation'  as jgdz
    ,src->>'legalPersonName' as fddbr
    ,src->>'businessScope' as jyfw
    ,src->>'industry'       as jjhy
    ,src->>'companyOrgType'  as jglx
    ,src->>'regCapital'  as zczj 
    ,src->>'regCapitalCurrency' as zczj_bz
    ,src->>'actualCapital'  as zczj_sj
    ,src->>'actualCapitalCurrency' as zczj_sj_bz
    ,src->>'taxNumber'  as taxdm
    ,to_timestamp((src->>'fromTime')::bigint/1000)::timestamp(6)  as fromtime 
    ,to_timestamp((src->>'toTime')::bigint/1000)::timestamp(6)   as totime
    ,src->>'regInstitute'   as djbumen
    ,src->>'regStatus'      as jyzt
    ,src->>'property3'       as engname
    ,src->>'bondNum'         as bondnum

    ,src->>'staffNumRange'    as zggm
    ,src->>'email'           as email
    ,src->>'phoneNumber'     as phone
    ,src->>'websiteList'      as website
    ,src->>'staffList'        as  staff_info
    ,src->>'alias'            as alias 

    ,src->>'revokeDate'      as diaoxiaodate
    ,src->>'revokeReason'      as diaoxiaoreason

    ,src->>'cancelDate'     as zhuxiaodate
    ,src->>'cancelReason'     as zhuxiaoreason

    ,src->>'logo'     as logo



     from ent.t_base_src  as b where not exists(select jgmc from ent.t_base_est as a where a.jgmc=regexp_replace(b.src->>'name','[^\u4E00-\u9FA5a-z0-9A-Z\(\)（）]','','g'))
     and src->>'name' is not null and coalesce(src->>'creditCode' ,src->>'regNumber',src->>'orgNumber' )  is not null
    """
    db_command(sql,dbtype="postgresql",conp=['postgres','since2015','192.168.4.188','bid','ent'])







#当ent表天添加了新的企业词,可更新 t_base_src  t_base_est 


def ent_tmp():
    sql="""insert into  "ent"."ent"(entname) 

    select distinct  word from ent.ent_tmp  as a where not exists(select 1 from ent.ent as b where a.word=b.entname)

    ;"""
    db_command(sql,dbtype="postgresql",conp=['postgres','since2015','192.168.4.188','bid','ent'])


def t_base_update():
    print("0、ent_tmp插入到ent")
    ent_tmp()
    print("1、 接口取数据 add_t_base_src")
    add_t_base_src()
    print("2、flush_tag1() 取到的将tag=1 ")
    flush_tag1()
    print("3、t_base_src2est 加载t_base_est ")
    t_base_src2est()