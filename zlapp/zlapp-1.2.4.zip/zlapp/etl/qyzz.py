from lmf.dbv2 import db_query ,db_command ,db_write 
from lmf.bigdata import pg2pg

from zlapp.zz.qiyezz import df2df 

#在schema里生成初始qyzz,依赖于jianzhu.gg_html表
def jianzhu_qyzz():
    sql="select * from jianzhu.gg_html  "

    conp=["postgres","since2015","192.168.4.188","bid","jianzhu"]

    pg2pg(sql,'qyzz',conp,conp,f=df2df,chunksize=1000)

#xzqh\zzcode\ent_key
def public_qyzz():
    conp=["postgres","since2015","192.168.4.188","bid","public"]
    sql="drop table if exists public.qyzz; "
    print(sql)
    db_command(sql,dbtype="postgresql",conp=conp)
    
    sql="""select *,public.zzname_to_zzcode(zzmc) as zzcode
    ,substring(tydm,3,4) as xzqh ,public.entname_to_key(entname) as ent_key
    into public.qy_zz 
     from jianzhu.qyzz"""
    print(sql)
    db_command(sql,dbtype="postgresql",conp=conp)


def est():
    print("开始从原始jianzhu.gg_html里解析qyzz")
    jianzhu_qyzz()

    print("原始qyzz，配上ent_key xzqh zzcode 入库")
    public_qyzz()


#速度 单机速度在1.5分钟1000，300*1.5=450分钟

##后续有一些补全空的操作