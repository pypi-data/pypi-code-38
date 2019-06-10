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

_name_="puyang"

# driver=webdriver.Chrome()

# url="http://www.pyggzy.com/list.asp?class=25&page=2"

# driver.get(url)

def f1(driver,num):
    locator=(By.CLASS_NAME,"lm_c")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    #url=driver.current_url
    cnum=int(driver.find_element_by_xpath("//td[@class='aspFont1']/font[2]").text) 
    if num!=cnum:
        url=re.sub("(?<=page=)[0-9]{1,}",str(num),driver.current_url)
        val=driver.find_element_by_xpath("//div[@class='lm_c']//table[1]//tr[1]//a").text.strip() 
        driver.get(url)

        locator=(By.XPATH,"//div[@class='lm_c']//table[1]//tr[1]//a[not(contains(string(),'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


    page=driver.page_source

    soup=BeautifulSoup(page,"html.parser")

    div=soup.find("div",class_="lm_c")

    tb=div.find("table")
    tb=tb.find("table")
    #ul=div.find("ul")
    trs=tb.find_all("tr")

    data=[]

    for li in trs:
        a=li.find("a")
        tds=li.find_all("td")
        tmp=[a.text.strip(),tds[-1].text.strip(),"http://www.pyggzy.com/"+a["href"]]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None

    return df 


def f2(driver):
    
    try:
        locator=(By.CLASS_NAME,"lm_c")
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


        total=int(driver.find_element_by_xpath("//td[@class='aspFont1']/font[3]").text)
    except:
        total=1
    driver.quit()
    return total



def f3(driver,url):


    driver.get(url)

    locator=(By.CLASS_NAME,"lm_c")

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

    div=soup.find('div',class_='lm_c')
    #div=div.find_all('div',class_='ewb-article')[0]
    
    return div

data=[

        ["gcjs_zhaobiao_gg","http://www.pyggzy.com/list.asp?class=25&page=1",["name","ggstart_time","href","info"],f1,f2],

      


        ["gcjs_zhongbiaohx_gg","http://www.pyggzy.com/list.asp?class=26&page=1",["name","ggstart_time","href","info"],f1,f2],

       

        ["zfcg_zhaobiao_gg","http://www.pyggzy.com/list.asp?class=34&page=1",["name","ggstart_time","href","info"],f1,f2],



        ["zfcg_zhongbiaohx_gg","http://www.pyggzy.com/list.asp?class=35&page=1",["name","ggstart_time","href","info"],f1,f2],

 

    ]

def work(conp,**args):
    est_meta(conp,data=data,diqu="河南省濮阳市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    work(conp=["postgres","since2015","127.0.0.1","henan","puyang"],num=1,total=2,html_total=10)