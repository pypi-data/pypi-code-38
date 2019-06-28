from lmf.dbv2 import db_query , db_command 
import traceback

#conp1 本地连接，conp2远程连接
#表gg_html 不存在则建表

def create_2tb(conp1):
    sql1="""
    create table if not exists  public.gg_html (
    html_key serial primary key ,
    href text , 
    page text, 
    quyu text
    )
    """
    db_command(sql=sql1,dbtype="postgresql",conp=conp1)
    sql2="""
    create table if not exists public.gg(
    gg_key serial primary key,
    name text,
    href text,
    ggstart_time text,
    ggtype  text,
    jytype  text,
    diqu text,
    info text,
    quyu text,
    create_time timestamp,
    update_time timestamp,
    html_key  bigint
    )
    """
    db_command(sql=sql2,dbtype="postgresql",conp=conp1)

#引入外部表
def create_ftbs(conp1,conp2):

    schema_sql="""select schema_name from information_schema.schemata 

    where schema_name !~ 'pg.*|public|information_schema'"""

    df=db_query(schema_sql,dbtype="postgresql",conp=conp2)

    arr=df["schema_name"].tolist()

    user,pwd,host,db=conp2[0],conp2[1],conp2[2],conp2[3]
    sql_tmp="""
    drop server if exists p_%s cascade ;
    create  server p_%s foreign data wrapper postgres_fdw options(host '%s',dbname'%s');
    create user mapping for postgres server p_%s options(user '%s',password'%s');
    """%(db,db,host,db,db,user,pwd)

    db_command(sql=sql_tmp,dbtype="postgresql",conp=conp1)
    for schema in arr:
        prefix="%s_%s"%(db,schema)
        tmp="""
        create foreign table fdw.%s_gg (
            name  text ,
            href text , 
            ggstart_time text ,
            ggtype text , 
            jytype text ,
            diqu text,
            info text     )
        server p_%s options(table_name'gg',schema_name'%s');
        create foreign table fdw.%s_gg_html (
          href text ,
            page text )
        server p_%s options(table_name'gg_html',schema_name'%s');
        """%(prefix,db,schema,prefix,db,schema)
        db_command(sql=tmp,dbtype="postgresql",conp=conp1)

#更新一个市
def update_shi(conp1,db,shi):
    quyu="%s_%s"%(db,shi)
    prefix1="%s_%s"%(db,shi)

    sql2="""
    insert into "public".gg_html(href,page,quyu)

    select href,page,'%s' as quyu from fdw.%s_gg_html  as a
    where not exists(select 1 from "public".gg_html as b where a.href=b.href and quyu ~'^%s.*')
    """%(quyu,prefix1,db)

    db_command(sql=sql2,dbtype="postgresql",conp=conp1)


    sql3="""with a as (SELECT * FRom fdw.%s_gg as t1
        where not exists ( 
        select 1 from "public".gg  as t2 where  t1.name=t2.name and t1.href=t2.href and t1.ggstart_time=t2.ggstart_time and quyu~'^%s.*')
        )

        ,b as (select * from "public".gg_html where quyu~'^%s.*')

        ,c as (select a.*,b.html_key from a left join b on a.href=b.href )

        insert into "public".gg (name,href,ggstart_time,diqu,ggtype,jytype,info,html_key,quyu,create_time,update_time)
        select name,href,ggstart_time,diqu,ggtype,jytype,info,html_key,'%s' as quyu,LOCALTIMESTAMP(0) as create_time, LOCALTIMESTAMP(0) as update_time from c
    """%(prefix1,db,db,quyu)
    db_command(sql=sql3,dbtype="postgresql",conp=conp1)



def update_sheng(conp1,conp2):
    """外部表已经存在"""
    create_ftbs(conp1,conp2)
    schema_sql="""select schema_name from information_schema.schemata 

    where schema_name !~ 'pg.*|public|information_schema'"""

    df=db_query(schema_sql,dbtype="postgresql",conp=conp2)
    arr=df["schema_name"].tolist()
    print(arr)
    for w in arr:
        try:
            print(w)
            update_shi(conp1,conp2[3],w)
        except:
            traceback.print_exc()





