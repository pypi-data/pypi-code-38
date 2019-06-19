from lmf.dbv2 import db_command,db_query 

def est_ggzhongbiao():
    sql="""
    create table if not exists public.gg_zhongbiao1
    (

    html_key bigint primary key  ,
    gg_fabutime timestamp(0)  ,

    gg_name  text ,

    zhongbiaoren text,
    zhongbiaojia   numeric(30,5),

    ggtype text ,
    href  text not null ,
    xmjl text,
    
    bd_key bigint,
    info text,
    quyu text
    )
    """
    conp=["postgres","since2015","192.168.4.188","bid","public"]
    db_command(sql,dbtype='postgresql',conp=conp)




def ggzhongbiao_update(tb):
    sql="""
    with t1 as (
    select distinct on (html_key) html_key,zhongbiaoren,zhongbiaojia,gg_fabutime,gg_name,ggtype,xmjl,href,info,quyu  from src.%s as t
    where  not exists (select 1 from gg_zhongbiao1 where gg_zhongbiao1.html_key=t.html_key) and zhongbiaoren is not null and html_key is not null ) 

    insert into public.gg_zhongbiao1(html_key,zhongbiaoren,zhongbiaojia,gg_fabutime,gg_name,ggtype,xmjl,href ,info,quyu)

    select * from t1 

    """%(tb)
    conp=["postgres","since2015","192.168.4.188","bid","public"]
    db_command(sql,dbtype='postgresql',conp=conp)

def update_alltb():
    sql="""
    SELECT tablename FROM pg_tables where schemaname='src' and tablename ~'b_gg'
    """
    conp=["postgres","since2015","192.168.4.188","bid","public"]

    df=db_query(sql,dbtype="postgresql",conp=conp)

    tbs=df['tablename'].values.tolist()

    for tb in tbs:
        print("抽取%s"%tb)
        ggzhongbiao_update(tb)
