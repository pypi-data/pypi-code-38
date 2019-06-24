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

_name_="jiyuan"

# driver=webdriver.Chrome()

# url="http://www.jyggjy.cn/TPFront/ZtbDetail/ZtbJsDetail.aspx?type=1&infoid=ecee9c5c-bde2-4f6f-8170-393aea4b89fd&categoryNum=005002001 "

# driver.get(url)

def f1(driver,num):
    locator=(By.XPATH,"//div[@class='morecontent']/table//tr//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    #url=driver.current_url
    cnum=int(re.findall("Paging=([0-9]{1,})",driver.current_url)[0])
    if num!=cnum:
        url=re.sub("(?<=Paging=)[0-9]{1,}",str(num),driver.current_url)
        val=driver.find_element_by_xpath("//div[@class='morecontent']//tr[1]//a").get_attribute("href")[-30:]
        driver.get(url)

        locator=(By.XPATH,"//div[@class='morecontent']//tr[1]//a[not(contains(@href,'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


    page=driver.page_source

    soup=BeautifulSoup(page,"html.parser")

    div=soup.find("div",class_="morecontent")
    #ul=div.find("ul")
    lis=div.find_all("tr",class_="trfont")

    data=[]

    for li in lis:
        a=li.find("a")
        ggstart_time=li.find_all("td")[-2].text.strip()
        tmp=[a["title"].strip(),ggstart_time,"http://www.jyggjy.cn"+a["href"]]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 


def f2(driver):
    
    try:
        locator=(By.CLASS_NAME,"pagemargin")
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

        total=driver.find_element_by_xpath("//div[@class='pagemargin']//td[@class='huifont']").text.split("/")[1]

       
        total=int(total)
    except:
        total=1
    driver.quit()
    return total



def f3(driver,url):


    driver.get(url)

    locator=(By.XPATH,"//div[contains(@id,'menutab')][not(contains(@style,'none'))]")

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

    div=soup.find('div',id=re.compile('menutab'),style=re.compile('^(?:(?<!none).)*$'))
    #div=div.find_all('div',class_='ewb-article')[0]
    
    return div

data=[

        ["gcjs_zhaobiao_gg","http://www.jyggjy.cn/TPFront/jyxx/005002/005002001/?Paging=1",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_biangeng_gg","http://www.jyggjy.cn/TPFront/jyxx/005002/005002002/?Paging=1",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiaohx_ruwei_gg","http://www.jyggjy.cn/TPFront/jyxx/005002/005002004/?Paging=1",["name","ggstart_time","href","info"],add_info(f1,{"ggtype":"入围公告"}),f2],

        ["gcjs_zhongbiaohx_gg","http://www.jyggjy.cn/TPFront/jyxx/005002/005002007/?Paging=1",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiao_gg","http://www.jyggjy.cn/TPFront/jyxx/005002/005002005/?Paging=1",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_liubiao_gg","http://www.jyggjy.cn/TPFront/jyxx/005002/005002006/?Paging=1",["name","ggstart_time","href","info"],f1,f2],




    ]

def work(conp,**args):
    est_meta(conp,data=data,diqu="河南省济源市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    work(conp=["postgres","since2015","192.168.4.175","henan","jiyuan"])