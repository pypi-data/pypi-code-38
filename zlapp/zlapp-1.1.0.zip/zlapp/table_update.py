from table import  gg_update_tmptb,gg_update_insert,gg_update_bdkey

from table import est_gghtml 

from lmf.dbv2 import db_command

def gg():
    print("一、更新t_gg_app ")
    conp_hawq=["gpadmin","since2015",'192.168.4.179','base_db',"v3"]
    conp_pg=["postgres","since2015",'192.168.4.188','bid',"cdc"]
    conp_pg1=["postgres","since2015",'192.168.4.188','bid',"public"]

    #gg_update_tmptb(conp_hawq,conp_pg)


    print("二、插入gg")

    gg_update_insert(conp_pg1)

    print("三、更新bd_key")
    gg_update_bdkey(conp_pg1)

    print("四、更新price 和中标人")


def gg_html():
    conp_pg1=["postgres","since2015",'192.168.4.188','bid',"public"]
    est_gghtml(conp_pg1)


def qy_zcry():

    sql="""drop table if exists public.qy_zcry;
    SELECT entname_to_key(entname) as ent_key
    ,entname_to_tydm(entname) tydm
    ,substring(entname_to_tydm(entname),3,6) as xzqh
    ,ryzz_to_code(zclb,zhuanye) as ryzz_code
    ,* 
    into public.qy_zcry
    FROM "cdc"."qy_zcry" ;
    """
    conp_pg1=["postgres","since2015",'192.168.4.188','bid',"public"]
    db_command(sql,dbtype="postgresql",conp=conp_pg1)


