from lmf.dbv2 import db_query ,db_command ,db_write 
from lmf.bigdata import pg2pg
from zlapp.ent.todb import add_t_ss_src


#将ss表中查到的entname-tag归1
def flush_tag1():
    sql="""
    update ent.ss as a set tag=1 where exists (select word from ent.t_ss_src as b where a.word=b.word);
    """
    db_command(sql,dbtype="postgresql",conp=['postgres','since2015','192.168.4.188','bid','ent'])



def t_ss_src2est():
    sql="""
truncate table ent.t_ss_est;
with a as (SELECT word
,json_array_elements(src::json->'items')->>'id'  as id
,regexp_replace(json_array_elements(src::json->'items')->>'name','</em>|<em>','','g') as entname 
,json_array_elements(src::json->'items')->>'base' as base
,json_array_elements(src::json->'items')->>'regCapital' as zczj
,json_array_elements(src::json->'items')->>'companyType' as jglx 
,json_array_elements(src::json->'items')->>'legalPersonName' as fddbr
,json_array_elements(src::json->'items')->>'type' as fddbr_type
, src::json->'items' as arr 
 FROM "ent"."t_ss_src")
,b as (
select distinct on (entname)   entname,id::bigint as id ,base,zczj,jglx,fddbr,fddbr_type,ent.calid(arr,id::bigint) as rk   from a

order by entname ,rk asc)
insert into ent.t_ss_est select * from b
;


    """
    db_command(sql,dbtype="postgresql",conp=['postgres','since2015','192.168.4.188','bid','ent'])


def ss_tmp():
    sql="""insert into  "ent"."ss"(word) 

    select distinct word from ent.ss_tmp  as a where not exists(select 1 from ent.ss as b where a.word=b.word)

    ;"""
    db_command(sql,dbtype="postgresql",conp=['postgres','since2015','192.168.4.188','bid','ent'])



def t_ss_update():
    print("0、ss_tmp插入到ss")
    ss_tmp()
    print("1、 接口取数据 add_t_ss_src")
    add_t_ss_src()
    print("2、flush_tag1() 取到的将tag=1 ")
    flush_tag1()
    print("3、t_ss_src2est 加载t_base_est ")
    t_ss_src2est()
