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

from collections import OrderedDict 

_name_="zhoukou"

# driver=webdriver.Chrome()

# url="http://www.zkggzyjy.gov.cn/TPFront/jyxx/002001/002001001/002001001003/?Paging=2"

# driver.get(url)

def f1(driver,num):
    locator=(By.XPATH,"//div[@style='height:500px;']")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    #url=driver.current_url
    cnum=int(re.findall("Paging=([0-9]{1,})",driver.current_url)[0])
    if num!=cnum:
        url=re.sub("(?<=Paging=)[0-9]{1,}",str(num),driver.current_url)
        val=driver.find_element_by_xpath("//div[@style='height:500px;']//tr[@height='25']//a").text.strip() 
        driver.get(url)

        locator=(By.XPATH,"//div[@style='height:500px;']//tr[@height='25']//a[not(contains(string(),'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


    page=driver.page_source

    soup=BeautifulSoup(page,"html.parser")

    div=soup.find("div",style='height:500px;')
    tbody=div.find("tbody")
    trs=tbody.find_all("tr",height='25')

    data=[]

    for tr in trs:
        a=tr.find("a")
        ggstart_time=tr.find("font").text.strip()
        tmp=[a["title"].strip(),ggstart_time,"http://www.zkggzyjy.gov.cn"+a["href"]]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 


def f2(driver):
    
    try:
        locator=(By.CLASS_NAME,"pagemargin")
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

        href=driver.find_element_by_xpath("//div[@class='pagemargin']").text

        total=re.findall("\/([0-9]{1,})",href)[0]
        total=int(total)
    except:
        total=1
    driver.quit()
    return total



def f3(driver,url):


    driver.get(url)

    locator=(By.ID,"tblInfo")

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

    div=soup.find('table',id='tblInfo')
    #div=div.find_all('div',class_='ewb-article')[0]
    
    return div




dztype=OrderedDict([("鹿邑县","001"),("项城市","002"),("川汇区","003"),("商水县","004"),("西华县","005"),("淮阳县","006")
,("太康县","007"),("扶沟县","008"),("郸城县","009"),("沈丘县","010"),("黄泛区","011"),("开发区","012"),("东新区","013"),("港区办","014")])

ggtype=OrderedDict([("zhaobiao","001"),("biangeng","002"),("zhongbiao","003"),("zhongbiaohx","004")])

data=[]

for w1 in ggtype.keys():
    for w2 in dztype.keys():
        p1="002001%s"%ggtype[w1]
        p2="002001%s%s"%(ggtype[w1],dztype[w2])
        href="http://www.zkggzyjy.gov.cn/zhoukou/jyxx/002001/%s/%s/?Paging=1"%(p1,p2)
        tmp=["gcjs_%s_diqu%s_gg"%(w1,dztype[w2]),href,["name","ggstart_time","href","info"],add_info(f1,{"diqu":w2}),f2]
        data.append(tmp)

ggtype1=OrderedDict([("zhaobiao","001"),("biangeng","002"),("zhongbiao","003")])
for w1 in ggtype1.keys():
    for w2 in dztype.keys():
        p1="002002%s"%ggtype1[w1]
        p2=["002002%s%s"%(ggtype1[w1],dztype[w2])]
        href="http://www.zkggzyjy.gov.cn/TPFront/jyxx/002002/%s/%s/?Pagin=1"%(p1,p2)
        tmp=["zfcg_%s_diqu%s_gg"%(w1,dztype[w2]),href,["name","ggstart_time","href","info"],add_info(f1,{"diqu":w2}),f2]






def work(conp,**args):
    est_meta(conp,data=data,diqu="河南省周口市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    work(conp=["postgres","since2015","127.0.0.1","henan","zhoukou"])
    #work(conp=["postgres","since2015","127.0.0.1","henan","zhoukou"],num=1,total=2,html_total=10)