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

_name_="xinxiang"



def f1(driver,num):
    locator=(By.XPATH,"//ul[@class='ewb-info-items']/li//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    #url=driver.current_url
    cnum=int(re.findall("([0-9]{1,}).html",driver.current_url)[0])
    if num!=cnum:
        url=re.sub("([0-9]{1,})(?=\.html)",str(num),driver.current_url)
        val=driver.find_element_by_xpath("//ul[@class='ewb-info-items']/li//a").text.strip() 
        driver.get(url)

        locator=(By.XPATH,"//ul[@class='ewb-info-items']/li//a[not(contains(string(),'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


    page=driver.page_source

    soup=BeautifulSoup(page,"html.parser")

    ul=soup.find("ul",class_="ewb-info-items")
    #ul=div.find("ul")
    lis=ul.find_all("li")

    data=[]

    for li in lis:
        a=li.find("a")
        ggstart_time=li.find("span").text.strip()
        tmp=[a["title"].strip(),ggstart_time,"http://www.xxggzy.cn"+a["href"]]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    fonts=a.find_all("font")
   
    info={"quyu":fonts[0].text.strip()}
    if len(fonts)>=3:
        info["gctype"]=fonts[2].text.strip()
    df["info"]=json.dumps(info,ensure_ascii=False)
    return df 


def f2(driver):
    
    try:
        locator=(By.XPATH,"//span[contains(@class,'ewb-page-number')]")
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

        txt=driver.find_element_by_xpath("//span[contains(@class,'ewb-page-number')]").text.strip().split('/')[1]

        total=int(txt)
    except:
        total=1
    driver.quit()
    return total



def f3(driver,url):
    driver.get(url)
    locator=(By.XPATH, "//div[@id='content']/div[contains(@style, 'margin-left')][string-length()>30]")
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
    div=soup.find('div',id='content')
    return div

data=[

        ["gcjs_zhaobiao_gg","http://www.xxggzy.cn/jyxx/089003/089003001/1.html",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_biangeng_gg","http://www.xxggzy.cn/jyxx/089003/089003002/1.html",["name","ggstart_time","href","info"],f1,f2],


        ["gcjs_zhongbiaohx_gg","http://www.xxggzy.cn/jyxx/089003/089003003/1.html",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_gqita_gg","http://www.xxggzy.cn/jyxx/089003/089003004/1.html",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhaobiao_gg","http://www.xxggzy.cn/jyxx/089004/089004001/1.html",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_biangeng_gg","http://www.xxggzy.cn/jyxx/089004/089004002/1.html",["name","ggstart_time","href","info"],f1,f2],


        ["zfcg_zhongbiaohx_gg","http://www.xxggzy.cn/jyxx/089004/089004003/1.html",["name","ggstart_time","href","info"],f1,f2],

    ]

def work(conp,**args):
    est_meta(conp,data=data,diqu="河南省新乡市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    work(conp=["postgres","since2015","192.168.3.171","henan","xinxiang"])