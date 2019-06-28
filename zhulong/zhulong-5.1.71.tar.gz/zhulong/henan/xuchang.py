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

_name_="xuchang"

# driver=webdriver.Chrome()

# url="http://www.pdsggzy.com/gzbgg/index_1.jhtml"

# driver.get(url)

def f1(driver,num):
    locator=(By.XPATH,"//div[@class='infolist-main']//li//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    #url=driver.current_url
    cnum=int(re.findall("index_([0-9]{1,}).jhtml",driver.current_url)[0])
    if num!=cnum:
        url=re.sub("(?<=index_)[0-9]{1,}",str(num),driver.current_url)
        val=driver.find_element_by_xpath("//div[@class='infolist-main']//li[1]//a").get_attribute('href')[-12:]
        driver.get(url)

        locator=(By.XPATH,"//div[@class='infolist-main']//li[1]//a[not(contains(@href,'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    page=driver.page_source
    soup=BeautifulSoup(page,"html.parser")
    div=soup.find("div",class_="infolist-main")
    ul=div.find("ul")
    lis=ul.find_all("li")
    data=[]
    for li in lis:
        a=li.find("a",recursive=False)
        
        spans=li.find_all("em")
        ggstart_time=spans[0].text.strip()
        tmp=[a["title"].strip(),ggstart_time,"http://ggzy.xuchang.gov.cn"+a["href"]]
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
    locator=(By.XPATH ,"//div[@class='s_content'][string-length()>50]")
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
    div=soup.find('div',class_='s_main')
    return div


data=[

        ["gcjs_zhaobiao_gg","http://ggzy.xuchang.gov.cn/gzbgg/index_1.jhtml",
         ["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_biangeng_gg","http://ggzy.xuchang.gov.cn/gbggg/index_1.jhtml",
         ["name","ggstart_time","href","info"],f1,f2],


        ["gcjs_zhongbiaohx_gg","http://ggzy.xuchang.gov.cn/gpbgs/index_1.jhtml",
         ["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiao_gg","http://ggzy.xuchang.gov.cn/gzbgs/index_1.jhtml",
         ["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_yucai_gg","http://ggzy.xuchang.gov.cn/zbqgs/index_1.jhtml",
         ["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhaobiao_gg","http://ggzy.xuchang.gov.cn/zzbgg/index_1.jhtml",
         ["name","ggstart_time","href","info"],f1,f2],

         ["zfcg_biangeng_gg","http://ggzy.xuchang.gov.cn/zbggg/index_1.jhtml",
          ["name","ggstart_time","href","info"],f1,f2],


        ["zfcg_zhongbiaohx_gg","http://ggzy.xuchang.gov.cn/zpsgs/index_1.jhtml",
         ["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhongbiao_gg","http://ggzy.xuchang.gov.cn/zzbgs/index_1.jhtml",
         ["name","ggstart_time","href","info"],f1,f2],


    ]


def work(conp,**args):
    est_meta(conp,data=data,diqu="河南省平许昌市",**args)
    est_html(conp,f=f3,**args)

# 网址更新：http://ggzy.xuchang.gov.cn/
# 更新日期：2019/6/28
if __name__=="__main__":
    work(conp=["postgres","since2015","192.168.3.171","henan","xuchang"],num=1,total=2,html_total=10,headless=False)


    # for d in data:
    #     url = d[1]
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #     d = f2(driver)
    #     print(d)
    #     driver=webdriver.Chrome()
    #     driver.get(url)
    #     df = f1(driver, 3)
    #     print(df.values)
    #     for i in df[2].values:
    #         f = f3(driver, i)
    #         print(f)