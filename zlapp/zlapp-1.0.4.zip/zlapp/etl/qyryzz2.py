from lmf.bigdata import pg2csv 
from fabric import Connection

def est_external_table():
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    sql="""create  external table cdc.jz_gg_html (href text,page text ) 
    location('gpfdist://192.168.4.187:8111/jz_gg_html.csv') format 'csv' (delimiter '\001' header quote '\002') log errors into errs segment reject limit 1000;  
    """
    db_command(sql,dbtype="postgresql",conp=conp)

def out_csv():
    path1=os.path.join("/data/lmf","jz_gg_html.csv")
    conp_src=["postgres","since2015","192.168.4.188",'bid','jianzhu']
    sql="""select href,replace(replace(replace(replace(page,'\001',''),'\002',''),'\r',''),'\n','') as page from jianzhu.gg_html """
    print(sql)
    pg2csv(sql,conp_src,path1,chunksize=5000,sep='\001',quotechar='\002')

def est_table_local():
    est_external_table()
    out_csv()

def est_table_remote():
    conp_remote=["root@192.168.4.187","rootHDPHAWQDatanode5@zhulong"]
    c=Connection(conp_remote[0],connect_kwargs={"password":conp_remote[1]})
    try:
        c.run("""/opt/python35/bin/python3 -c "from zlapp.etl.qyryzz2 import est_table_local;est_table_local() " """,pty=True,encoding='utf8')
    except:
        traceback.print_exc()
    finally:
        c.close()
