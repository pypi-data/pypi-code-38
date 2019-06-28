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
_name_="zhongshan"


def f1(driver,num):
    locator=(By.XPATH,"//div[@class='nav_list']//li[1]//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    url=driver.current_url

    cnum=re.findall("jsp\?page=([0-9]{1,})",url)[0]
    if num!=cnum:
        val=driver.find_element_by_xpath("//div[@class='nav_list']//li[1]//a").text 

        url=re.sub("(?<=page=)[0-9]{1,}",str(num),url)
        locator=(By.XPATH,"//div[@class='nav_list']//li[1]//a[string()!='%s']"%val)
        driver.get(url)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    page=driver.page_source 
    soup=BeautifulSoup(page,"html.parser")

    div=soup.find("div",class_='nav_list')

    lis=div.find_all("li",class_="clear")
    data=[]
    for li in lis:
        a=li.find("a")
        span=li.find("span")
        tmp=[a["title"],span.text.strip(),"http://www.zsjyzx.gov.cn"+a["href"]]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 

def f2(driver):
    locator=(By.XPATH,"//div[@class='nav_list']//li[1]//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    locator=(By.XPATH,"//div[@class='f-page']//li[@class='pageintro']")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    li=driver.find_element_by_xpath("//div[@class='f-page']//li[@class='pageintro']").text
    total=re.findall("共([0-9]{1,})页",li)[0]
    total=int(total)
    driver.quit()
    return total


def f3(driver,url):

    driver.get(url)
    driver.switch_to.frame(0)

    locator=(By.CLASS_NAME,"articalDiv")

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

    div=soup.find('div',class_="articalDiv")
    #div=div.find_all('div',class_='ewb-article')[0]
    
    return div


data=[

        ["gcjs_zhaobiao_gg","http://www.zsjyzx.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=58",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiaohx_gg","http://www.zsjyzx.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=60",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiao_gg","http://www.zsjyzx.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=61",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_gqita_gg","http://www.zsjyzx.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=107",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhaobiao_gg","http://www.zsjyzx.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=4",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhongbiao_gg","http://www.zsjyzx.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=55",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_biangeng_gg","http://www.zsjyzx.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=54",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_liubiao_gg","http://www.zsjyzx.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=138",["name","ggstart_time","href","info"],f1,f2]

    ]



def work(conp,**args):
    est_meta(conp,data=data,diqu="广东省中山市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","127.0.0.1","guangdong","zhongshan"])