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

_name_="wugang"

# driver=webdriver.Chrome()

# url="http://www.wgggzy.net/Content/jsgc?pageIndex=1"

# driver.get(url)

def f1(driver,num):
    locator=(By.XPATH,"//div[@class='filter-content']/ul/li//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    #url=driver.current_url
    cnum=int(re.findall("pageIndex=([0-9]{1,})",driver.current_url)[0])
    if num!=cnum:
        url=re.sub("(?<=pageIndex=)[0-9]{1,}",str(num),driver.current_url)
        val=driver.find_element_by_xpath("//div[@class='filter-content']/ul/li[1]//a").get_attribute('href')[-20:] 
        driver.get(url)

        locator=(By.XPATH,"//div[@class='filter-content']/ul/li[1]//a[not(contains(@href,'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


    page=driver.page_source

    soup=BeautifulSoup(page,"html.parser")

    div=soup.find("div",class_="filter-content")
    ul=div.find("ul")
    lis=ul.find_all("li")

    data=[]

    for li in lis:
        a=li.find("a")
        ggstart_time=a.find("span",class_="time").text.strip()
        tmp=[a["title"].strip(),ggstart_time,"http://www.wgggzy.net"+a["href"]]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 


def f2(driver):
    
    try:
        locator=(By.CLASS_NAME,"pagination")
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

        href=driver.find_element_by_xpath("//ul[@class='pagination']//li[last()]/a").get_attribute('href')

        total=re.findall("pageIndex=([0-9]{1,})",href)[0]
        total=int(total)
    except:
        total=1
    driver.quit()
    return total



def f3(driver,url):


    driver.get(url)

    locator=(By.CLASS_NAME,"content")

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

    div=soup.find('div',class_='content',style=re.compile("padding.*"))
    #div=div.find_all('div',class_='ewb-article')[0]
    
    return div

data=[

        ["gcjs_zhaobiao_gg","http://www.wgggzy.net/Content/jsgc?pageIndex=1",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_biangeng_gg","http://www.wgggzy.net/BidNotice/jsgc/bggg?pageIndex=1",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_kaibiao_gg","http://www.wgggzy.net/BidNotice/jsgc/kbqk?pageIndex=1",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiaohx_gg","http://www.wgggzy.net/BidNotice/jsgc/zbhxrgs?pageIndex=1",["name","ggstart_time","href","info"],f1,f2],

        

        ["zfcg_zhaobiao_gg","http://www.wgggzy.net/BidNotice/zfcg/cggg?pageIndex=1",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_biangeng_gg","http://www.wgggzy.net/BidNotice/zfcg/bggg?pageIndex=1",["name","ggstart_time","href","info"],f1,f2],


        ["zfcg_zhongbiaohx_gg","http://www.wgggzy.net/BidNotice/zfcg/zbjggg?pageIndex=1",["name","ggstart_time","href","info"],f1,f2],


    ]

def work(conp,**args):
    est_meta(conp,data=data,diqu="河南省舞钢市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    work(conp=["postgres","since2015","127.0.0.1","henan","wugang"])
    #work(conp=["postgres","since2015","127.0.0.1","henan","wugang"],num=1,total=2,html_total=10)