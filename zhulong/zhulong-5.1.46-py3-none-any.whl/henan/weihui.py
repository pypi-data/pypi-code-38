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

_name_="weihui"

# driver=webdriver.Chrome()

# url="http://www.whggzy.cn/ggxx/jzgc/zbgg/"

# driver.get(url)

def f1(driver,num):
    locator=(By.XPATH,"//ul[@class='list_m_style']/li//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    if re.search('\/[0-9]{1,}\/',url) is  None:
        cnum=1
    else:
        cnum=int(re.findall('\/([0-9]{1,})\/',url)[0])

    if num!=cnum:
        if num==1:
            url=re.sub('[0-9]{1,}\/','',url)
        elif cnum!=1:
            url=re.sub('(?<=\/)[0-9]{1,}(?=\/)',str(num),url)
        else:
            url=url+"%s/"%str(num)
        val=driver.find_element_by_xpath("//ul[@class='list_m_style']/li[1]//a").get_attribute('href')[-20:]
        driver.get(url)

        locator=(By.XPATH,"//ul[@class='list_m_style']/li[1]//a[not(contains(@href,'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


    page=driver.page_source

    soup=BeautifulSoup(page,"html.parser")

    ul=soup.find("ul",class_="list_m_style")
    #ul=div.find("ul")
    lis=ul.find_all("li",class_='list_m_li')

    data=[]

    for li in lis:
        a=li.find("a")
        ggstart_time=a.find("span").text.strip()
        tmp=[list(a.strings)[0],ggstart_time,"http://www.whggzy.cn"+a["href"]]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 


def f2(driver):
    
    try:
        locator=(By.CLASS_NAME,"k_pagelist")
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

        href=driver.find_element_by_xpath("//span[@class='k_pagelist']/a[last()]").text

        total=re.findall("[0-9]{1,}",href)[0]
        total=int(total)
    except:
        total=1
    driver.quit()
    return total



def f3(driver,url):


    driver.get(url)

    locator=(By.CLASS_NAME,"art_content")

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

    div=soup.find('div',class_='art_content')
    #div=div.find_all('div',class_='ewb-article')[0]
    
    return div

data=[

        ["gcjs_zhaobiao_gg","http://www.whggzy.cn/ggxx/jzgc/zbgg/",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_biangeng_gg","http://www.whggzy.cn/ggxx/jzgc/bggg/",["name","ggstart_time","href","info"],f1,f2],


        ["gcjs_zhongbiaohx_gg","http://www.whggzy.cn/ggxx/zfcg/jggs/",["name","ggstart_time","href","info"],f1,f2],

 

        ["zfcg_zhaobiao_gg","http://www.whggzy.cn/ggxx/zfcg/zbgg/",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_biangeng_gg","http://www.whggzy.cn/ggxx/zfcg/bggg/",["name","ggstart_time","href","info"],f1,f2],


        ["zfcg_zhongbiaohx_gg","http://www.whggzy.cn/ggxx/zfcg/jggs/",["name","ggstart_time","href","info"],f1,f2],


    ]

def work(conp,**args):
    est_meta(conp,data=data,diqu="河南省卫辉市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    work(conp=["postgres","since2015","127.0.0.1","henan","weihui"],num=1,total=2,html_total=10)