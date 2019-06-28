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

_name_="nanyang"


def f1(driver,num):
    locator=(By.XPATH,"//ul[@class='wb-data-item']//li//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    #url=driver.current_url
    cnum=int(re.findall("Paging=([0-9]{1,})",driver.current_url)[0])
    if num!=cnum:
        url=re.sub("(?<=Paging=)[0-9]{1,}",str(num),driver.current_url)
        val=driver.find_element_by_xpath("//ul[@class='wb-data-item']//li[1]//a").text.strip() 
        driver.get(url)

        locator=(By.XPATH,"//ul[@class='wb-data-item']//li[1]//a[not(contains(string(),'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


    page=driver.page_source

    soup=BeautifulSoup(page,"html.parser")

    ul=soup.find("ul",class_="wb-data-item")
    #ul=div.find("ul")
    lis=ul.find_all("li")

    data=[]

    for li in lis:
        a=li.find("a")
        
        span=li.find("span")
        ggstart_time=span.text.strip()
        tmp=[a["title"].strip(),ggstart_time,"http://www.nyggzyjy.cn"+a["href"]]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 


def f2(driver):
    
    try:
        locator=(By.CLASS_NAME,"pagemargin")
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

        

        txt=driver.find_element_by_class_name("pagemargin").text
        total=re.findall("\/([0-9]{1,})",txt)[0]
        total=int(total)
    except:
        total=1
    driver.quit()
    return total



def f3(driver,url):
    driver.get(url)
    locator=(By.XPATH,"//table[@id='tblInfo'][string-length()>30]")
    WebDriverWait(driver,20).until(EC.presence_of_all_elements_located(locator))

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
    div=soup.find('table',id='tblInfo')
    return div


data=[
    ["gcjs_zhaobiao_gg","http://www.nyggzyjy.cn/TPFront/jyxx/004001/004001001/?Paging=1",["name","ggstart_time","href","info"],f1,f2],

    ["gcjs_biangeng_gg","http://www.nyggzyjy.cn/TPFront/jyxx/004001/004001002/?Paging=1",["name","ggstart_time","href","info"],f1,f2],

    ["gcjs_zhongbiaohx_gg","http://www.nyggzyjy.cn/TPFront/jyxx/004001/004001003/?Paging=1",["name","ggstart_time","href","info"],f1,f2],

    ["gcjs_zhongbiaohx_gg","http://www.nyggzyjy.cn/TPFront/jyxx/004001/004001004/?Paging=1",["name","ggstart_time","href","info"],f1,f2],

    ["zfcg_zhaobiao_gg","http://www.nyggzyjy.cn/TPFront/jyxx/004002/004002001/?Paging=1",["name","ggstart_time","href","info"],f1,f2],

    ["zfcg_biangeng_gg","http://www.nyggzyjy.cn/TPFront/jyxx/004002/004002002/?Paging=1",["name","ggstart_time","href","info"],f1,f2],

    ["zfcg_zhongbiaohx_gg","http://www.nyggzyjy.cn/TPFront/jyxx/004002/004002003/?Paging=1",["name","ggstart_time","href","info"],f1,f2],
    ]


def work(conp,**args):
    est_meta(conp,data=data,diqu="河南省南阳市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    work(conp=["postgres","since2015","192.168.3.171","henan","nanyang"])