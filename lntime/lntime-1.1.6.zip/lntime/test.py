from lmf.dbv2 import db_query 
from bs4 import BeautifulSoup 
import re
from common import exttime_fpage,exttime_guangdong_zhongshan
#from route import exttime 
def getpage(href,quyu):
    arr=quyu.split('_')
    db,schema=arr[0],'_'.join(arr[1:])

    conp=['postgres','since2015','192.168.4.175',db,schema]
    sql="select page from %s.gg_html where href='%s' "%(schema,href)
    df=db_query(sql,dbtype="postgresql",conp=conp)

    page=df.iat[0,0]
    return page

href="http://www.zsjyzx.gov.cn/Application/NewPage/PageArtical_1.jsp?nodeID=53&articalID=94112"
page=getpage(href,'guangdong_zhongshan')

#date2=exttime('2019-05-02',page,'guangdong_zhongshan')
date2=exttime_guangdong_zhongshan(page)
date1= exttime_fpage(page)

soup=BeautifulSoup(page,'lxml')


