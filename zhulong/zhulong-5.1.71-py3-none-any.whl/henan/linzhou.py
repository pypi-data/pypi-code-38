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

_name_="linzhou"

# driver=webdriver.Chrome()

# url="http://www.ayggzy.cn/jyxx/jsgcZbgg"

# driver.get(url)

def f1(driver,num):
    locator=(By.XPATH,"//table[@id='p2']//tr[2]//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    #url=driver.current_url
    cnum=int(driver.find_element_by_xpath("//div[@class='mmggxlh']//a[@class='cur']").text)
    if num!=cnum:
        
        val=driver.find_element_by_xpath("//table[@id='p2']//tr[2]//a").get_attribute("href")[-50:]

        driver.execute_script("pagination(%d);"%num)

        locator=(By.XPATH,"//table[@id='p2']//tr[2]//a[not(contains(@href,'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


    page=driver.page_source

    soup=BeautifulSoup(page,"html.parser")

    table=soup.find("table",id="p2")
   
    trs=table.find_all("tr")[1:]

    data=[]

    for tr in trs:
        a=tr.find("a")
        tds=tr.find_all("td")
        ggstart_time=tr.find_all('td')[-1].text.strip()
        tmp=[a["title"].strip(),ggstart_time,"http://www.ayggzy.cn"+a["href"]]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    if len(tds)==4:
        df["info"]=json.dumps({"bh":tds[1].text.strip()},ensure_ascii=False)
    else:
        df["info"]=None
    return df 


def f2(driver):
    locator=(By.XPATH,"//table[@id='p2']//tr[2]//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    locator=(By.CLASS_NAME,"mmggxlh")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    total=int(driver.find_element_by_xpath("//div[@class='mmggxlh']//a[last()-1]").text)
    driver.quit()
    return total



def f3(driver,url):
    driver.get(url)
    locator=(By.CLASS_NAME,"content_all_nr")
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

    div=soup.find('div',class_='content_all_nr')
    #div=div.find_all('div',class_='ewb-article')[0]
    
    return div

data=[
        ["gcjs_zhaobiao_gg","http://www.ayggzy.cn/jyxx/jsgcZbgg",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_biangeng_gg","http://www.ayggzy.cn/jyxx/jsgcBgtz",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiaohx_gg","http://www.ayggzy.cn/jyxx/jsgcZbjggs",["name","ggstart_time","href","info"],f1,f2],


        ["zfcg_yucai_gg","http://www.ayggzy.cn/jyxx/zfcg/ygg",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhaobiao_gg","http://www.ayggzy.cn/jyxx/zfcg/cggg",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_biangeng_gg","http://www.ayggzy.cn/jyxx/zfcg/gzsx",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhongbiaohx_gg","http://www.ayggzy.cn/jyxx/zfcg/zbjggs",["name","ggstart_time","href","info"],f1,f2],
    ]

def work(conp,**args):
    est_meta(conp,data=data,diqu="河南省林州市",**args)
    est_html(conp,f=f3,**args)

# 修改日期：2019/6/28
if __name__=="__main__":
    work(conp=["postgres","since2015","127.0.0.1","henan","linzhou"])

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