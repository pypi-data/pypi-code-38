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

_name_="jiyuan1"

# driver=webdriver.Chrome()

# url="http://www.jyggjy.cn/TPFront/jyxx/005003/005003001/"

# driver.get(url)

def f1(driver,num):
    locator=(By.XPATH,"//ul[@class='wb-data-item']//li//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    #url=driver.current_url
    cnum=int(driver.find_element_by_xpath("//ul[@class='wb-page-items clearfix']/li/a[contains(@class,'current')]").text.strip())
    if num!=cnum:
        

        val=driver.find_element_by_xpath("//ul[@class='wb-data-item']//li[1]//a").get_attribute("href")[-30:]
        driver.execute_script("ShowAjaxNewPage(window.location.pathname,'categorypagingcontent',%d)"%num)

        locator=(By.XPATH,"//ul[@class='wb-data-item']//li[1]//a[not(contains(@href,'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


    page=driver.page_source

    soup=BeautifulSoup(page,"lxml")

    div=soup.find("ul",class_="wb-data-item")
    #ul=div.find("ul")
    lis=div.find_all("li",class_="wb-data-list")

    data=[]

    for li in lis:
        a=li.find("a")
        ggstart_time=li.find("span",class_="wb-data-date").text.strip()
        tmp=[a.text.strip(),ggstart_time,"http://www.jyggjy.cn"+a["href"]]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 


def f2(driver):
    
    try:
        locator=(By.CLASS_NAME,"wb-page-number")
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

        total=driver.find_element_by_xpath("//a[contains(@class,'wb-page-number')]").text.split("/")[1]

       
        total=int(total)
    except:
        total=1
    driver.quit()
    return total



def f3(driver,url):


    driver.get(url)

    locator=(By.CLASS_NAME,"article-block")

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

    div=soup.find('div',class_="article-block")
    #div=div.find_all('div',class_='ewb-article')[0]
    
    return div

data=[

        ["zfcg_zhaobiao_gg","http://www.jyggjy.cn/TPFront/jyxx/005003/005003001/",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_biangeng_gg","http://www.jyggjy.cn/TPFront/jyxx/005003/005003002/",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhongbiaohx_gg","http://www.jyggjy.cn/TPFront/jyxx/005003/005003005/",["name","ggstart_time","href","info"],f1,f2],



        ["zfcg_liubiao_gg","http://www.jyggjy.cn/TPFront/jyxx/005003/005003006/",["name","ggstart_time","href","info"],f1,f2],




    ]

def work(conp,**args):
    est_meta(conp,data=data,diqu="河南省济源市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    work(conp=["postgres","since2015","127.0.0.1","henan","jiyuan1"])