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

href="http://ggj.huainan.gov.cn/HNWeb_NEW/ZtbInfo/ZtbDyDetail_zfcg.aspx?InfoID=17579d42-d0df-44a6-801d-fc909f1cb0c8&type=3zfcg&categoryNum=002002002003"
page=getpage(href,'anhui_huainan')

date1= exttime_fpage(page)

soup=BeautifulSoup(page,'lxml')


