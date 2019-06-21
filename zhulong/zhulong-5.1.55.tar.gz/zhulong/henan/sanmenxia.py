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
from collections import OrderedDict
import sys 
import time

import json
from zhulong.util.etl import gg_meta,gg_html,est_meta,est_html

_name_="sanmenxia"

# driver=webdriver.Chrome()

# url="http://www.smxgzjy.org/zbgg/index_1.jhtml"

# driver.get(url)

def f1(driver,num):
    locator=(By.XPATH,"//div[@class='List1']//li//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    #url=driver.current_url
    cnum=int(re.findall("index_([0-9]{1,}).jhtml",driver.current_url)[0])
    if num!=cnum:
        url=re.sub("(?<=index_)[0-9]{1,}",str(num),driver.current_url)
        val=driver.find_element_by_xpath("//div[@class='List1']//li[1]//a").text.strip() 
        driver.get(url)

        locator=(By.XPATH,"//div[@class='List1']//li[1]//a[not(contains(string(),'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


    page=driver.page_source

    soup=BeautifulSoup(page,"html.parser")

    div=soup.find("div",class_="List1")
    ul=div.find("ul")
    lis=ul.find_all("li")

    data=[]

    for li in lis:
        a=li.find("a",recursive=False)
        
        spans=li.find_all("span")
        ggstart_time=spans[0].text.strip()
        tmp=[a.text.strip(),ggstart_time,"http://www.smxgzjy.org"+a["href"]]
        # info={"quyu":spans[1].find("a").text}
        # tmp.append(json.dumps(info,ensure_ascii=False))
        data.append(tmp)
    df=pd.DataFrame(data=data)

    df["info"]=None
    return df 


def f2(driver):
    
    try:
        locator=(By.XPATH,"//div[@class='Top10 TxtCenter']")
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

        

        txt=driver.find_element_by_xpath("//div[@class='Top10 TxtCenter']").text
        total=re.findall("\/([0-9]{1,})页",txt)[0]
        total=int(total)
    except:
        total=1
    driver.quit()
    return total



def f3(driver,url):


    driver.get(url)

    locator=(By.XPATH,"//div[@class='Center W980 WhiteBg Padding10']")

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

    div=soup.find('div',class_='Center W980 WhiteBg Padding10')
    #div=div.find_all('div',class_='ewb-article')[0]
    
    return div


data=[

        ["gcjs_zhaobiao_gg","http://www.smxgzjy.org/zbgg/index_1.jhtml",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_biangeng_gg","http://www.smxgzjy.org/jbggg/index_1.jhtml",["name","ggstart_time","href","info"],f1,f2],


        ["gcjs_kongzhijia_gg","http://www.smxgzjy.org/jlbj/index_1.jhtml",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiaohx_gg","http://www.smxgzjy.org/zbgs/index_1.jhtml",["name","ggstart_time","href","info"],f1,f2],




        

        ["zfcg_zhaobiao_gg","http://www.smxgzjy.org/cggg/index_1.jhtml",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_biangeng_gg","http://www.smxgzjy.org/bggg/index_1.jhtml",["name","ggstart_time","href","info"],f1,f2],


        ["zfcg_zhongbiaohx_gg","http://www.smxgzjy.org/jggg/index_1.jhtml",["name","ggstart_time","href","info"],f1,f2],


    ]


def work(conp,**args):
    est_meta(conp,data=data,diqu="河南省三门峡市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    work(conp=["postgres","since2015","127.0.0.1","henan","sanmenxia"],num=1,total=2,html_total=10,pageloadtimeout=60)