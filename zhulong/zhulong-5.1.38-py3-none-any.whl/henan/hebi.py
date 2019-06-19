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

_name_="hebi"

# driver=webdriver.Chrome()

# url="http://ggzy.hebi.gov.cn/TPFront/gcjs/013001/?Paging=1"

# driver.get(url)

def f1(driver,num):
    locator=(By.XPATH,"//td[@class='border3']//tr//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    #url=driver.current_url
    cnum=int(re.findall("Paging=([0-9]{1,})",driver.current_url)[0])
    if num!=cnum:
        url=re.sub("(?<=Paging=)([0-9]{1,})",str(num),driver.current_url)
        val=driver.find_element_by_xpath("//td[@class='border3']//tr[1]//a").text.strip() 
        driver.get(url)

        locator=(By.XPATH,"//td[@class='border3']//tr[1]//a[not(contains(string(),'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


    page=driver.page_source

    soup=BeautifulSoup(page,"html.parser")

    div=soup.find("td",class_="border3")
    #ul=div.find("ul")
    trs=div.find_all("tr",height="30")

    data=[]

    for tr in trs:
        a=tr.find("a")
        ggstart_time=tr.find_all("td")[-1].text.strip()
        tmp=[a["title"].strip(),ggstart_time,"http://ggzy.hebi.gov.cn"+a["href"]]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 


def f2(driver):
    
    try:
        locator=(By.CLASS_NAME,"pagemargin")
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

        total=driver.find_element_by_xpath("//td[@class='huifont']").text.split("/")[1]

        
        total=int(total)
    except:
        total=1
    driver.quit()
    return total



def f3(driver,url):
    driver.get(url)
    locator=(By.XPATH,"//div[contains(@id, 'menutab')][string-length()>30] | //td[@width='998'][string-length()>30]")
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
    div = soup.find('div', id=re.compile('menutab_\d+_\d+'), style='')
    if div ==  None:
        div = soup.find('td', width='998')
    return div

data=[
        ["gcjs_zhaobiao_gg","http://ggzy.hebi.gov.cn/TPFront/gcjs/013001/?Paging=1",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_biangeng_gg","http://ggzy.hebi.gov.cn/TPFront/gcjs/013002/?Paging=1",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiaohx_gg","http://ggzy.hebi.gov.cn/TPFront/gcjs/013003/?Paging=1",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiao_gg","http://ggzy.hebi.gov.cn/TPFront/gcjs/013004/?Paging=1",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_yucai_gg","http://ggzy.hebi.gov.cn/TPFront/zfcg/014001/?Paging=1",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhaobiao_gg","http://ggzy.hebi.gov.cn/TPFront/zfcg/014002/?Paging=1",["name","ggstart_time","href","info"],f1,f2],
        ["zfcg_biangeng_gg","http://ggzy.hebi.gov.cn/TPFront/zfcg/014003/?Paging=1",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhongbiaohx_gg","http://ggzy.hebi.gov.cn/TPFront/zfcg/014004/?Paging=1",["name","ggstart_time","href","info"],f1,f2],

    ]

def work(conp,**args):
    est_meta(conp,data=data,diqu="河南省鹤壁市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    work(conp=["postgres","since2015","192.168.3.171","henan","hebi"])
    #
    #
    # driver = webdriver.Chrome()
    # df = f3(driver, 'http://ggzy.hebi.gov.cn/TPFront/showinfo/ZtbJyxxDetail.aspx?type=3&InfoID=32cf314e-ef38-4f88-a55b-31d87c561b6e&CategoryNum=014004')
    # print(df)