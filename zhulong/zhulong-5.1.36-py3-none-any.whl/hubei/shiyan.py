
import pandas as pd  
import re 

from selenium import webdriver 
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_query,db_command
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 

from zhulong.util.etl import est_meta,est_html,add_info
import time 
_name_="shiyan"


def f1(driver,num):
    if num==1:
        num="index"
    url=driver.current_url
    if ".html" not in url:
        url=url+"%s.html"%str(num)
    else:
        url=re.sub("(?<=/)[0-9]{1,}(?=.html)",str(num),url)
    driver.get(url)
    locator=(By.CLASS_NAME,"list_content")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page=driver.page_source
    i=3
    time.sleep(1)
    while len(page)!=len(driver.page_source):
        i-=1
        page=driver.page_source 
        time.sleep(1)
        if i<0:break 

    soup=BeautifulSoup(page,'html.parser')

    divs=soup.find_all("div",class_="list_cloumn")
    data=[]

    for div in divs:
        href=div["onclick"]
        href=re.findall("\('(.*html)'\)",href)[0]
        lis=div.find_all("li")
        a=lis[0].find("a")["title"]
        rq=re.findall("[0-9\-:]{1,}\s[0-9\-:]{1,}",lis[2].text)[0]
        tmp=[a,rq,href]
        data.append(tmp)
    df=pd.DataFrame(data)
    df["info"]=None
    return df 


def f2(driver):
    locator=(By.ID,"pages")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total=driver.find_element_by_xpath("//div[@id='pages']//a[last()-1]").text
    total=int(total)
    driver.quit()
    return total


def f3(driver,url):


    driver.get(url)

    locator=(By.CLASS_NAME,"display_content")

    WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))

    before=len(driver.page_source)
    time.sleep(0.1)
    after=len(driver.page_source)
    i=0
    while before!=after:
        before=len(driver.page_source)
        time.sleep(0.1)
        after=len(driver.page_source)
        i+=1
        if i>5:break

    page=driver.page_source

    soup=BeautifulSoup(page,'html.parser')

    div=soup.find('div',class_='display_content')
    #div=div.find_all('div',class_='ewb-article')[0]
    
    return div





data=[
    ["gcjs_zhaobiao_gg","http://www.syggzyjyzx.org.cn/html/jyxx/gongcheng/zbgg/",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_zhongbiao_gg","http://www.syggzyjyzx.org.cn/html/jyxx/gongcheng/zbgs/",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_kongzhijia_gg","http://www.syggzyjyzx.org.cn/html/jyxx/gongcheng/zgxj/",["name","ggstart_time","href","info"],f1,f2],

    ["zfcg_zhaobiao_gg","http://www.syggzyjyzx.org.cn/html/jyxx/zhengcai/caigougonggao/",["name","ggstart_time","href","info"],f1,f2],
    ["zfcg_zhongbiao_gg","http://www.syggzyjyzx.org.cn/html/jyxx/zhengcai/chengjiaogonggao/",["name","ggstart_time","href","info"],f1,f2],
]

def work(conp,**args):
    est_meta(conp,data,diqu="湖北省十堰市",**args)
    est_html(conp,f=f3,**args)

if __name__=='__main__':
    work(conp=["postgres","since2015","127.0.0.1","hubei","shiyan"])
