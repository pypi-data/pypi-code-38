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
from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, add_info

_name_="pingdingshan"

# driver=webdriver.Chrome()

# url="http://www.pdsggzy.com/zzbgg/index_1.jhtml"

# driver.get(url)

def f1(driver,num):
    locator=(By.XPATH,"//div[@class='infolist-main']//li//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    #url=driver.current_url
    cnum=int(re.findall("index_([0-9]{1,}).jhtml",driver.current_url)[0])
    if num!=cnum:
        url=re.sub("(?<=index_)[0-9]{1,}",str(num),driver.current_url)
        val=driver.find_element_by_xpath("//div[@class='infolist-main']//li[1]//a").text.strip() 
        driver.get(url)

        locator=(By.XPATH,"//div[@class='infolist-main']//li[1]//a[not(contains(string(),'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


    page=driver.page_source

    soup=BeautifulSoup(page,"html.parser")

    div=soup.find("div",class_="infolist-main")
    ul=div.find("ul")
    lis=ul.find_all("li")

    data=[]

    for li in lis:
        a=li.find("a")
        
        span=a.find("em")
        ggstart_time=span.text.strip()
        tmp=[a["title"].strip(),ggstart_time,"http://www.pdsggzy.com"+a["href"]]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 


def f2(driver):
    
    try:
        locator=(By.CLASS_NAME,"TxtCenter")
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

        

        txt=driver.find_element_by_class_name("TxtCenter").text
        total=re.findall("\/([0-9]{1,})页",txt)[0]
        total=int(total)
    except:
        total=1
    driver.quit()
    return total



def f3(driver,url):


    driver.get(url)

    locator=(By.XPATH ,"//div[@class='s_content'][string-length()>200]")

    WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))

    before=len(driver.page_source)
    time.sleep(0.5)
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

    div=soup.find('div',class_='s_main')

    
    return div


data=[
        ["gcjs_zhaobiao_gg","http://www.pdsggzy.com/zzbgg/index_1.jhtml",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_kongzhijia_gg","http://www.pdsggzy.com/jzbkzjgg/index_1.jhtml",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiaohx_gg","http://www.pdsggzy.com/gzbgs/index_1.jhtml",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_gqita_yuzhaobiao_gg","http://www.kfsggzyjyw.cn/zbqgs/index_1.jhtml",["name","ggstart_time","href","info"],add_info(f1, {'gglx':'标前公告'}),f2],

        ["zfcg_zhaobiao_gg","http://www.pdsggzy.com/zzbgg/index_1.jhtml",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_biangeng_gg","http://www.kfsggzyjyw.cn/zbggg/index_1.jhtml",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhongbiaohx_gg","http://www.pdsggzy.com/zzbgs/index_1.jhtml",["name","ggstart_time","href","info"],f1,f2],
    ]


def work(conp,**args):
    est_meta(conp,data=data,diqu="河南省平顶山市",**args)
    est_html(conp,f=f3,**args)

# 修改日期：2019/6/28
if __name__=="__main__":
    work(conp=["postgres","zhulong.com.cn","192.168.169.47","henan","pingdingshan"],num=1,total=2,pageloadstrategy='none',headless=False)