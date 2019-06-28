import pandas as pd  
import re 

from selenium import webdriver 
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 


import json

import time

from zhulong.util.etl import est_html,est_meta ,add_info
_name_="zhuhai"

def f1(driver,num):
    locator=(By.CLASS_NAME,"rl-box-right")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=int(re.findall("index_([0-9]{1,}).jhtml",url)[0])
    locator=(By.XPATH,"//div[@class='rl-box-right']/ul/li[1]/a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    val=driver.find_element_by_xpath("//div[@class='rl-box-right']/ul/li[1]/a").text
    if cnum!=num:
        url=re.sub("(?<=index_)[0-9]{1,}(?=.jhtml)",str(num),url)
        driver.get(url)
        locator=(By.XPATH,"//div[@class='rl-box-right']/ul/li[1]/a[string()!='%s']"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    page=driver.page_source 

    soup=BeautifulSoup(page,"html.parser")

    div=soup.find("div",class_="rl-box-right")

    ul=div.find("ul")
    lis=ul.find_all("li",recursive=False)
    data=[]

    for li in lis:
        a=li.find("a")
        tmp=[a["title"],a["href"],li.find("span").text.strip()]
        data.append(tmp)
    df=pd.DataFrame(data)
    df["info"]=None
    return df 


def f2(driver):
    locator=(By.CLASS_NAME,"rl-box-right")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    locator=(By.XPATH,"//div[@class='rl-box-right']/ul/li[1]/a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    info=driver.find_element_by_xpath("//div[@class='pagesite']").text
    total=re.findall("记录[\s0-9]{1,2}/([0-9]{1,})页",info)[0]
    total=int(total)
    driver.quit()
    return total


def f3(driver,url):

    driver.get(url)

    locator=(By.CLASS_NAME,"newsTex")

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

    div=soup.find('div',class_="newsTex")
    #div=div.find_all('div',class_='ewb-article')[0]
    
    return div

data=[
        ["gcjs_zhaobiao_gg","http://ggzy.zhuhai.gov.cn/zbgg/index_1.jhtml",["name","href","ggstart_time","info"],f1,f2],

        ["gcjs_zhongbiaohx_gg","http://ggzy.zhuhai.gov.cn/pbjggs/index_1.jhtml",["name","href","ggstart_time","info"],f1,f2],

        ["gcjs_zhongbiao_gg","http://ggzy.zhuhai.gov.cn/zbgs/index_1.jhtml",["name","href","ggstart_time","info"],f1,f2],

        ["gcjs_zhongbiao_1_gg","http://ggzy.zhuhai.gov.cn/zbjj/index_1.jhtml",["name","href","ggstart_time","info"],f1,f2],

        ["gcjs_biangeng_gg","http://ggzy.zhuhai.gov.cn/zbwjxg/index_1.jhtml",["name","href","ggstart_time","info"],f1,f2],

        ["gcjs_liubiao_gg","http://ggzy.zhuhai.gov.cn/zbzz/index_1.jhtml",["name","href","ggstart_time","info"],f1,f2],


        ["zfcg_zhaobiao_gg","http://ggzy.zhuhai.gov.cn/cggg/index_1.jhtml",["name","href","ggstart_time","info"],f1,f2],

        ["zfcg_biangeng_gg","http://ggzy.zhuhai.gov.cn/gzgg/index_1.jhtml",["name","href","ggstart_time","info"],f1,f2],

        ["zfcg_zhongbiaohx_gg","http://ggzy.zhuhai.gov.cn/yzbgg/index_1.jhtml",["name","href","ggstart_time","info"],f1,f2],

        ["zfcg_zhongbiao_gg","http://ggzy.zhuhai.gov.cn/zczbgg/index_1.jhtml",["name","href","ggstart_time","info"],f1,f2]
    ]


def work(conp,**args):
    est_meta(conp,data=data,diqu="广东省珠海市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","127.0.0.1","guangdong","zhuhai"])