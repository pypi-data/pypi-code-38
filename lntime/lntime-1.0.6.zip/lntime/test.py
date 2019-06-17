from lmf.dbv2 import db_query 
from bs4 import BeautifulSoup 
import re
from common import exttime_fpage

def getpage(href,quyu):
    arr=quyu.split('_')
    db,schema=arr[0],'_'.join(arr[1:])

    conp=['postgres','since2015','192.168.4.175',db,schema]
    sql="select page from %s.gg_html where href='%s' "%(schema,href)
    df=db_query(sql,dbtype="postgresql",conp=conp)

    page=df.iat[0,0]
    return page

href="http://aqggzy.anqing.gov.cn/jyxx/012001/012001002/20151021/9ca04652-6ab7-46f1-b157-60789251fbb2.html"
page=getpage(href,'anhui_anqing')


soup=BeautifulSoup(page,'lxml')


