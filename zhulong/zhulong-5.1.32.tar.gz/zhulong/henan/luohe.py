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

_name_="luohe"

# driver=webdriver.Chrome()

# url="https://www.lhjs.cn/BidNotice/jsgc/zbgg?pageIndex=1"

# driver.get(url)

def f1(driver,num):
    locator=(By.XPATH,"//div[@class='filter-content']//li//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    #url=driver.current_url
    cnum=int(re.findall("pageIndex=([0-9]{1,})",driver.current_url)[0])
    if num!=cnum:
        url=re.sub("(?<=pageIndex=)[0-9]{1,}",str(num),driver.current_url)
        val=driver.find_element_by_xpath("//div[@class='filter-content']//li[1]//a").text.strip() 
        driver.get(url)

        locator=(By.XPATH,"//div[@class='filter-content']//li[1]//a[not(contains(string(),'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


    page=driver.page_source

    soup=BeautifulSoup(page,"html.parser")

    div=soup.find("div",class_="filter-content")
    ul=div.find("ul")
    lis=ul.find_all("li")

    data=[]

    for li in lis:
        a=li.find("a")
        
        span=li.find("span",class_="time")
        ggstart_time=span.text.strip()
        tmp=[a["title"].strip(),ggstart_time,"https://www.lhjs.cn"+a["href"]]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 


def f2(driver):
    
    try:
        locator=(By.CLASS_NAME,"pagination")
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

        

        txt=driver.find_element_by_xpath("//ul[@class='pagination']//li/a[contains(string(),'尾页')]").get_attribute("href")
        total=re.findall("pageIndex=([0-9]{1,})",txt)[0]
        total=int(total)
    except:
        total=1
    driver.quit()
    return total



def f3(driver,url):


    driver.get(url)
    # try:
    #     locator=(By.XPATH,"//div[@class='Center W980 WhiteBg Padding10']")

    #     WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))
    # except:
    #     pass

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
    locator=(By.XPATH,"//div[@class='inner-main-content'][string-length(string())>10]")

    WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))
    page=driver.page_source

    soup=BeautifulSoup(page,'html.parser')

    div=soup.find('div',class_='inner-main-content')

    #div=div.find_all('div',class_='ewb-article')[0]
    
    return div


data=[

        ["gcjs_zhaobiao_gg","https://www.lhjs.cn/BidNotice/jsgc/zbgg?pageIndex=1",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_biangeng_gg","https://www.lhjs.cn/BidNotice/jsgc/bggg?pageIndex=1",["name","ggstart_time","href","info"],f1,f2],


        ["gcjs_kaibiao_gg","https://www.lhjs.cn/BidNotice/jsgc/bggg?pageIndex=1",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiaohx_gg","https://www.lhjs.cn/BidNotice/jsgc/zbhxrgs?pageIndex=1",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiao_gg","https://www.lhjs.cn/BidNotice/jsgc/zbjggg?pageIndex=1",["name","ggstart_time","href","info"],f1,f2],



        

        ["zfcg_zhaobiao_gg","https://www.lhjs.cn/BidNotice/zfcg/cggg?pageIndex=1",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_biangeng_gg","https://www.lhjs.cn/BidNotice/zfcg/bggg?pageIndex=1",["name","ggstart_time","href","info"],f1,f2],


        ["zfcg_zhongbiaohx_gg","https://www.lhjs.cn/BidNotice/zfcg/zbjggg?pageIndex=1",["name","ggstart_time","href","info"],f1,f2],


    ]


def work(conp,**args):
    est_meta(conp,data=data,diqu="河南省漯河市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    work(conp=["postgres","since2015","127.0.0.1","henan","luohe"])