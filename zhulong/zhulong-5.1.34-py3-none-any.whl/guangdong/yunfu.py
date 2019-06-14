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
_name_="yunfu"


def f1(driver,num):
    locator=(By.XPATH,"//ul[@class='r-items']/li//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    url=driver.current_url 
    cnum=int(re.findall("Paging=([0-9]{1,})",url)[0])
    if num!=cnum:
        val=driver.find_element_by_xpath("//ul[@class='r-items']/li//a").text
        url=re.sub("(?<=Paging=)[0-9]{1,}",str(num),url)
        driver.get(url)
        locator=(By.XPATH,"//ul[@class='r-items']/li//a[string()!='%s']"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    page=driver.page_source 
    soup=BeautifulSoup(page,"html.parser")

    ul=soup.find("ul",class_='r-items')
    lis=ul.find_all("li",class_='clearfix')

    data=[]
    for li in lis:
        a=li.find("a")
        span=li.find("span")
        tmp=[a["title"],span.text.strip(),"http://ggzy.yunfu.gov.cn"+a["href"]]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 

def f2(driver):
    locator=(By.XPATH,"//ul[@class='r-items']/li//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    val=driver.find_element_by_xpath("//div[@class='pagemargin']//td[@class='huifont']").text

    total=int(val.split("/")[1])

    driver.quit()
    return total


def f3(driver,url):

    driver.get(url)

    locator=(By.XPATH,"//div[@data-role='tab-content'][@class=''] | //div[@class='post-content'][string-length()>50]")

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
    div= soup.find("div",class_="post-con")
    if div == None:
        div=soup.find('div',attrs={"data-role":"tab-content","class":""})

    return div


data=[
        ["gcjs_zhaobiao_gg","http://ggzy.yunfu.gov.cn/yfggzy/jsgc/002001/?Paging=1",["name","ggstart_time","href","info"],f1,f2],
        ["gcjs_zhongbiaohx_gg","http://ggzy.yunfu.gov.cn/yfggzy/jsgc/002003/?Paging=1",["name","ggstart_time","href","info"],f1,f2],
        ["gcjs_biangeng_gg","http://ggzy.yunfu.gov.cn/yfggzy/jsgc/002002/?Paging=1",["name","ggstart_time","href","info"],f1,f2],
        ["gcjs_zhongbiao_gg","http://ggzy.yunfu.gov.cn/yfggzy/jsgc/002005/?Paging=1",["name","ggstart_time","href","info"],f1,f2],


        ["zfcg_zhaobiao_gg","http://ggzy.yunfu.gov.cn/yfggzy/zfcg/003001/?Paging=1",["name","ggstart_time","href","info"],f1,f2],
        ["zfcg_biangeng_gg","http://ggzy.yunfu.gov.cn/yfggzy/zfcg/003002/?Paging=1",["name","ggstart_time","href","info"],f1,f2],
        ["zfcg_zhongbiaohx_gg","http://ggzy.yunfu.gov.cn/yfggzy/zfcg/003003/?Paging=1",["name","ggstart_time","href","info"],f1,f2],
        ["zfcg_liubiao_gg","http://ggzy.yunfu.gov.cn/yfggzy/zfcg/003007/?Paging=1",["name","ggstart_time","href","info"],f1,f2],
        ["zfcg_zhaobiao_danyilaiyuan_gg","http://ggzy.yunfu.gov.cn/yfggzy/zfcg/003006/?Paging=1",["name","ggstart_time","href","info"],add_info(f1,{"zbfs":"单一来源"}),f2],
        ["zfcg_gqita_gg","http://ggzy.yunfu.gov.cn/yfggzy/zfcg/003005/?Paging=1",["name","ggstart_time","href","info"],f1,f2],



    ]


def work(conp,**args):
    est_meta(conp,data=data,diqu="广东省云浮市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","127.0.0.1","guangdong","yunfu"])