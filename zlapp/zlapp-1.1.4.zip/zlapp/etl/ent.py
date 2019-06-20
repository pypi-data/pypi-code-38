from lmf.dbv2 import db_query ,db_command ,db_write 
from lmf.bigdata import pg2pg
from zlapp.ent.todb import add_t_base_src


#企业相关表 


#1 接口加入新的数据

#将ent表中查不到的entname-tag归零
def flush_tag0():
   
    sql="""
    update public.ent as a set tag=0 where not exists (select jgmc from cdc.t_base_src as b where a.entname=b.jgmc);
    """
    db_command(sql,dbtype="postgresql",conp=['postgres','since2015','192.168.4.188','bid','cdc'])
#add_t_base_src
#将ent表中查到的entname-tag归1
def flush_tag1():
    sql="""
    update public.ent as a set tag=1 where exists (select jgmc from cdc.t_base_src as b where a.entname=b.jgmc);
    """
    db_command(sql,dbtype="postgresql",conp=['postgres','since2015','192.168.4.188','bid','cdc'])

#通过 t_base_est 将ent 表里tydm补充
def ent_update_tydm():
    sql="""
    update public.ent set tydm=public.tbase_entname_to_tydm(entname) where tydm is null and tag=1
    """
    db_command(sql,dbtype="postgresql",conp=['postgres','since2015','192.168.4.188','bid','cdc'])



#src2est
def t_base_src2est():
    sql="""
    insert into cdc.t_base_est
    select 
    jgmc
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



     from t_base_src  as b where not exists(select jgmc from cdc.t_base_est as a where a.jgmc=b.jgmc)
    """
    db_command(sql,dbtype="postgresql",conp=['postgres','since2015','192.168.4.188','bid','cdc'])



#当ent表天添加了新的企业词

def t_base_update():
    print("1、 接口取数据 add_t_base_src")
    add_t_base_src()
    print("2、flush_tag1() 取到的将tag=1 ")
    flush_tag1()
    print("3、t_base_src2est 加载t_base_est ")
    t_base_src2est()
    print("4、刷一下ent 表里的tydm")
    ent_update_tydm()