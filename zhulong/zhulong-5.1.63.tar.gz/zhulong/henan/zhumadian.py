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

_name_="zhumadian"

# driver=webdriver.Chrome()

# url="http://www.zmdggzy.gov.cn/TPFront/jyxx/003001/003001002/003001002001/"

# driver.get(url)

def f1(driver,num):
    locator=(By.XPATH,"//ul[@class='ewb-data-item']")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    #url=driver.current_url
    try:
        cnum=int(driver.find_element_by_xpath("//a[contains(@class,'current')]").text)
    except:
        cnum=1
    #cnum=int(driver.find_element_by_xpath("//a[contains(@class,'current')]").text)
    if num!=cnum:
       
        val=driver.find_element_by_xpath("//ul[@class='ewb-data-item']//li[1]//a").text.strip() 
        input1=driver.find_element_by_id("GoToPagingNo")
        input1.clear()
        input1.send_keys(num)
        driver.execute_script("GoToPaging();")

        locator=(By.XPATH,"//ul[@class='ewb-data-item']//li[1]//a[not(contains(string(),'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


    page=driver.page_source

    soup=BeautifulSoup(page,"html.parser")

    ul=soup.find("ul",class_='ewb-data-item')

    lis=ul.find_all("li")

    data=[]

    for li in lis:
        a=li.find("a")
        ggstart_time=li.find("span").text.strip()
        tmp=[a.text.strip(),ggstart_time,"http://www.zmdggzy.gov.cn"+a["href"]]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 


def f2(driver):
    
    try:
        locator=(By.CLASS_NAME,"ewb-page-number")
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

        href=driver.find_element_by_class_name("ewb-page-number").text

        total=re.findall("\/([0-9]{1,})",href)[0]
        total=int(total)
    except:
        total=1
    driver.quit()
    return total



def f3(driver,url):


    driver.get(url)

    locator=(By.ID,"categorypagingcontent")

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

    div=soup.find('div',id='categorypagingcontent')
    #div=div.find_all('div',class_='ewb-article')[0]
    
    return div



def get_data():

    dztype=OrderedDict([("驻马店市","001"),("西平县","002"),("上蔡县","003"),("平舆县","004"),("正阳县","005"),("确山县","006")
    ,("泌阳县","007"),("汝南县","008"),("遂平县","009")])

    ggtype=OrderedDict([("zhaobiao","001"),("zgys","002"),("biangeng","003"),("liubiao","004"),("zhongbiaohx","005")])

    data=[]

    for w1 in ggtype.keys():
        for w2 in dztype.keys():
            p1="003001%s"%ggtype[w1]
            p2="003001%s%s"%(ggtype[w1],dztype[w2])
            href="http://www.zmdggzy.gov.cn/TPFront/jyxx/003001/%s/%s/"%(p1,p2)
            tmp=["gcjs_%s_diqu%s_gg"%(w1,dztype[w2]),href,["name","ggstart_time","href","info"],add_info(f1,{"diqu":w2}),f2]
            data.append(tmp)

    ggtype1=OrderedDict([("zhaobiao","001"),("yucai","002"),("biangeng","003"),("zhongbiao","004"),("liubiao","005")])
    for w1 in ggtype1.keys():
        for w2 in dztype.keys():
            p1="003002%s"%ggtype1[w1]
            p2=["003002%s%s"%(ggtype1[w1],dztype[w2])]
            href="http://www.zmdggzy.gov.cn/TPFront/jyxx/003002/%s/%s/"%(p1,p2)
            tmp=["zfcg_%s_diqu%s_gg"%(w1,dztype[w2]),href,["name","ggstart_time","href","info"],add_info(f1,{"diqu":w2}),f2]

    data1=data.copy()
    arr=["gcjs_zgys_diqu005_gg","gcjs_zgys_diqu009_gg"]
    for w in data:
        if w[0] in arr:data1.remove(w)
    return data1

data=get_data()




def work(conp,**args):
    est_meta(conp,data=data,diqu="河南省驻马店市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    work(conp=["postgres","since2015","127.0.0.1","henan","zhumadian"])
    #work(conp=["postgres","since2015","127.0.0.1","henan","zhumadian"],num=1,total=2,html_total=10)