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
from zhulong.util.etl import gg_meta,gg_html,est_meta,est_html,add_info

from collections import OrderedDict 

_name_="yanshi"

# driver=webdriver.Chrome()

# url="http://www.yssggzyjy.cn/TPFront/ShowInfo/MoreInfoListjygg.aspx?categoryNum=002001001"

# driver.get(url)

def f1(driver,num):
    locator=(By.XPATH,"//ul[@class='ewb-bd-items']")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    #url=driver.current_url
    cnum=int(driver.find_element_by_class_name("redfont").text)
    if num!=cnum:
       
        val=driver.find_element_by_xpath("//ul[@class='ewb-bd-items']//li[1]//a").text.strip() 
        input1=driver.find_element_by_id("GoToPagingNo")
        input1.clear()
        input1.send_keys(num)
        driver.execute_script("GoToPaging();")

        locator=(By.XPATH,"//ul[@class='ewb-bd-items']//li[1]//a[not(contains(string(),'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


    page=driver.page_source

    soup=BeautifulSoup(page,"html.parser")

    ul=soup.find("ul",class_='ewb-bd-items')

    lis=ul.find_all("li")

    data=[]

    for li in lis:
        a=li.find("a")
        ggstart_time=li.find("span").text.strip()
        #name=a.text.strip()
        #name=re.sub("\[.*\]","",name)
        tmp=[a["title"].strip(),ggstart_time,"http://www.yssggzyjy.cn"+a["href"]]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 


def f2(driver):
    
    try:
        locator=(By.CLASS_NAME,"pagemargin")
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

        href=driver.find_element_by_class_name("pagemargin").text

        total=re.findall("\/([0-9]{1,})",href)[0]
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

    div=soup.find('div',class_='article-block')
    #div=div.find_all('div',class_='ewb-article')[0]
    
    return div



data=[
    ["gcjs_zhaobiao_gg","http://www.yssggzyjy.cn/TPFront/ShowInfo/MoreInfoListjygg.aspx?categoryNum=002001001",["name","ggstart_time","href","info"],f1,f2],

    ["gcjs_biangeng_gg","http://www.yssggzyjy.cn/TPFront/ShowInfo/MoreInfoListjygg.aspx?categoryNum=002001002",["name","ggstart_time","href","info"],f1,f2],

    ["gcjs_zhongbiaohx_gg","http://www.yssggzyjy.cn/TPFront/ShowInfo/MoreInfoListjygg.aspx?categoryNum=002001003",["name","ggstart_time","href","info"],f1,f2],

    ["gcjs_zhongbiao_gg","http://www.yssggzyjy.cn/TPFront/ShowInfo/MoreInfoListjygg.aspx?categoryNum=002001004",["name","ggstart_time","href","info"],f1,f2],

    ["gcjs_liubiao_gg","http://www.yssggzyjy.cn/TPFront/ShowInfo/MoreInfoListjygg.aspx?categoryNum=002001005",["name","ggstart_time","href","info"],f1,f2],

   ["zfcg_liubiao_gg","http://www.yssggzyjy.cn/TPFront/ShowInfo/MoreInfoListjygg.aspx?categoryNum=002002003",["name","ggstart_time","href","info"],f1,f2],

    ["zfcg_zhaobiao_gg","http://www.yssggzyjy.cn/TPFront/ShowInfo/MoreInfoListjygg.aspx?categoryNum=002002001",["name","ggstart_time","href","info"],f1,f2],

    ["zfcg_biangeng_gg","http://www.yssggzyjy.cn/TPFront/ShowInfo/MoreInfoListjygg.aspx?categoryNum=002002002",["name","ggstart_time","href","info"],f1,f2],

    ["zfcg_zhongbiaohx_gg","http://www.yssggzyjy.cn/TPFront/ShowInfo/MoreInfoListjygg.aspx?categoryNum=002002004",["name","ggstart_time","href","info"],f1,f2],


]






def work(conp,**args):
    est_meta(conp,data=data,diqu="河南省偃师市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    work(conp=["postgres","since2015","127.0.0.1","henan","yanshi"])