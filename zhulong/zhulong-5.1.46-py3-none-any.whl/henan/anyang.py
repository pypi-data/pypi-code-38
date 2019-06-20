import pandas as pd  
import re 

from selenium import webdriver 
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_command,db_query
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 

import sys 
import time

import json
from zhulong.util.etl import gg_meta,gg_html,est_meta,est_html

_name_="anyang"

# driver=webdriver.Chrome()

# url="http://www.ayggzy.cn/jyxx/jsgcZbgg?city="

# driver.get(url)

def f1(driver,num):
    locator=(By.ID,"p2")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    #url=driver.current_url
    cnum=int(driver.find_element_by_class_name("cur").text) 
    if num!=cnum:
        
        val=driver.find_element_by_xpath("//table[@id='p2']//tr/td//a").text.strip() 
        driver.execute_script("pagination(%s);return false;"%str(num))
        locator=(By.XPATH,"//table[@id='p2']//tr/td//a[not(contains(string(),'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


    page=driver.page_source

    soup=BeautifulSoup(page,"html.parser")

    div=soup.find("table",id="p2")
    #ul=div.find("ul")
    lis=div.find_all("tr")

    data=[]

    for li in lis[1:]:
        a=li.find("a")
        tds=li.find_all("td")
        tmp=[a["title"].strip(),tds[-1].text.strip(),"http://www.ayggzy.cn"+a["href"]]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    if len(tds)==4:
        df["info"]=json.dumps({"bh":tds[1].text.strip()},ensure_ascii=False)
    else:
        df["info"]=None
    return df 


def f2(driver):
    
    locator=(By.CLASS_NAME,"mmggxlh")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    try:

        txt=driver.find_element_by_class_name("mmggxlh").text

        total=re.findall("([0-9]{1,})\s下一页",txt)[0]
        total=int(total)
    except:
        total=1
    driver.quit()
    return total



def f3(driver,url):


    driver.get(url)

    locator=(By.CLASS_NAME,"content_all_nr")

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

    div=soup.find('div',class_='content_all_nr')
    #div=div.find_all('div',class_='ewb-article')[0]
    
    return div

data=[

        ["gcjs_zhaobiao_gg","http://www.ayggzy.cn/jyxx/jsgcZbgg",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_biangeng_gg","http://www.ayggzy.cn/jyxx/jsgcBgtz?city=",["name","ggstart_time","href","info"],f1,f2],


        ["gcjs_zhongbiaohx_gg","http://www.ayggzy.cn/jyxx/jsgcZbjggs?city=",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_yucai_gg","http://www.ayggzy.cn/jyxx/zfcg/ygg?city=",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhaobiao_gg","http://www.ayggzy.cn/jyxx/zfcg/cggg?city=",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_biangeng_gg","http://www.ayggzy.cn/jyxx/zfcg/gzsx?city=",["name","ggstart_time","href","info"],f1,f2],


        ["zfcg_zhongbiaohx_gg","http://www.ayggzy.cn/jyxx/zfcg/zbjggs?city=",["name","ggstart_time","href","info"],f1,f2],

        ["yiliao_zhaobiao_gg","http://www.ayggzy.cn/jyxx/ypyx/toListPage?type=1&city=",["name","ggstart_time","href","info"],f1,f2],

        ["yiliao_biangeng_gg","http://www.ayggzy.cn/jyxx/ypyx/toListPage?type=2&city=",["name","ggstart_time","href","info"],f1,f2],

        ["yiliao_zhongbiaohx_gg","http://www.ayggzy.cn/jyxx/ypyx/toListPage?type=3&city=",["name","ggstart_time","href","info"],f1,f2],

    ]

def work(conp,**args):
    est_meta(conp,data=data,diqu="河南省安阳市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    work(conp=["postgres","since2015","127.0.0.1","henan","anyang"],num=1,total=2,html_total=10)