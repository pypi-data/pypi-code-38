import os 
from zlhawq.data import zhulong_diqu_dict ,zl_diqu_dict
import time 
from lmf.dbv2 import db_command
import traceback
#先在hawq etl 的schema里生成近一个月的数据 目前的更新机制是半天一更新
#早上6点，下午三点

def t_gg_app_prt1():
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    print("t_gg_app_prt1部分，先清空")
    sql="truncate etl.t_gg_app_prt1"

    db_command(sql,dbtype="postgresql",conp=conp)
    total=sum([len(zhulong_diqu_dict[sheng]) for sheng in zhulong_diqu_dict.keys() ])
    costs=0
    bg=time.time()
    for sheng in zhulong_diqu_dict.keys():
        quyus=zhulong_diqu_dict[sheng]
        
        
        for quyu in quyus:
            try:
                print("开始注入quyu----%s"%quyu)
                sql="""
                insert into etl.t_gg_app_prt1
                select *   from v3.t_gg where quyu='%s'

                and fabu_time>='2019-05-28' and fabu_time<'2019-07-28'

                """%(quyu)
                db_command(sql,dbtype="postgresql",conp=conp)

                
            except:
                traceback.print_exc()
            finally:
                total-=1
                ed=time.time()
                cost=int(ed-bg)
                costs+=cost
                print("耗时----%s秒,还剩%d个,总耗时%d秒"%(cost,total,costs))
                bg=time.time()

    print("gcjs  zfcg 部分")
    arr=['gcjs','zfcg']
    total=sum([len(zl_diqu_dict[sheng]) for sheng in  arr ])
    costs=0
    bg=time.time()
    for sheng in arr:
        quyus=zl_diqu_dict[sheng]
        
        
        for quyu in quyus:
            try:
                print("开始注入quyu----%s"%quyu)
                sql="""
                insert into etl.t_gg_app_prt1
                select *   from v3.t_gg where quyu='%s'

                and fabu_time>='2019-05-28' and fabu_time<'2019-07-28'

                """%(quyu)
                db_command(sql,dbtype="postgresql",conp=conp)

                
            except:
                traceback.print_exc()
            finally:
                total-=1
                ed=time.time()
                cost=int(ed-bg)
                costs+=cost
                print("耗时----%s秒,还剩%d个,总耗时%d秒"%(cost,total,costs))
                bg=time.time()




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


