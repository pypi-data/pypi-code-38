import os 


#先在hawq etl 的schema里生成近一个月的数据 目前的更新机制是半天一更新
#早上6点，下午三点
def gg_update_tmptb(conp_hawq,conp_pg,tbname='t_gg_app'):

    bgdate=datetime.strftime(datetime.now()-timedelta(days=30),'%Y-%m-%d')

    eddate=datetime.strftime(datetime.now()+timedelta(days=365),'%Y-%m-%d')

    bg=time.time()
    sql="""select * from v3.t_gg where fabu_time>='%s'  and fabu_time<'%s' and quyu not in('zlsys_yunnan_kunming') 
    union all 
    select * from v3.t_gg where quyu in ('zlsys_yunnan_kunming') 
    """%(bgdate,eddate)

    datadict={"html_key":BIGINT(),'guid':TEXT(),"gg_name":TEXT(),"href":TEXT(),"fabu_time":TIMESTAMP(),"ggtype":TEXT(),
    "jytype":TEXT(),"diqu":TEXT(),"quyu":TEXT(),"info":TEXT(),"page":TEXT(),"create_time":TIMESTAMP()}
    pg2pg(sql,tbname,conp_hawq,conp_pg,chunksize=5000,datadict=datadict)
    ed=time.time()
    cost=int(ed-bg)
    print("耗时%s秒"%cost)


