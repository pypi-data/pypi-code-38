from lmf.dbv2 import db_query ,db_command ,db_write 
from lmf.bigdata import pg2pg

from zlapp.zz.zcry import df2df 

def jianzhu_qyzcry():
    sql="select ryxx_href,ryxx_name,sex,id_type,id_number,zyzcxx from jianzhu.jianzhu_ryxx_html  "
    conp1=["postgres","since2015","192.168.4.188","bid","jianzhu"]
    conp2=["postgres","since2015","192.168.4.188","bid","jianzhu"]

    pg2pg(sql,"qyzcry",conp1,conp2,f=df2df,chunksize=10000,if_exists='replace')


##增加person_key  ent_key ryzz_code  xzqh tydm 