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
from zhulong.util.etl import gg_meta,gg_html,est_meta,est_html,add_info

_name_="luoyang"

#driver=webdriver.Chrome()

# url="http://www.lyggzyjy.cn/TPFront/jyxx/009001/009001001/009001001001/?Paging=1"

# driver.get(url)

def f1(driver,num):
    locator=(By.XPATH,"//ul[@class='ewb-data-item']/li//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    #url=driver.current_url
    cnum=int(re.findall("Paging=([0-9]{1,})$",driver.current_url)[0])
    if num!=cnum:
        url=re.sub("(?<=Paging=)[0-9]{1,}",str(num),driver.current_url)
        val=driver.find_element_by_xpath("//ul[@class='ewb-data-item']/li[1]//a").text.strip() 
        driver.get(url)

        locator=(By.XPATH,"//ul[@class='ewb-data-item']/li[1]//a[not(contains(string(),'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


    page=driver.page_source

    soup=BeautifulSoup(page,"html.parser")

    div=soup.find("ul",class_="ewb-data-item")
    #ul=div.find("ul")
    lis=div.find_all("li")

    data=[]

    for li in lis:
        a=li.find("a")
        
        span=li.find_all("span",recursive=False)[0]
        ggstart_time=span.text.strip()
        tmp=[a["title"].strip(),ggstart_time,"http://www.lyggzyjy.cn"+a["href"]]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 


def f2(driver):
    
    try:
        locator=(By.CLASS_NAME,"huifont")
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

        

        total=driver.find_element_by_class_name("huifont").text.split("/")[1]
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


def get_data():
    data=[]

    ggtype=OrderedDict([("zhaobiao","001"),("biangeng","002"),("zhongbiaohx","003")])

    dztype=OrderedDict([("市本级","001"),("涧西区","002"),("偃师市","003"),("洛宁县","004"),("孟津县","005")
    ,("新安县","006"),("宜阳县","007"),("伊川县","008"),("嵩县","009"),("汝阳县","010") ])

    for w1 in ggtype.keys():
        for w2 in dztype.keys():
            p1="009001%s"%ggtype[w1]
            p2="009001%s%s"%(ggtype[w1],dztype[w2])
            href="http://www.lyggzyjy.cn/TPFront/jyxx/009001/%s/%s/?Paging=1"%(p1,p2)
            tmp=["gcjs_%s_diqu%s_gg"%(w1,dztype[w2]),href,["name","ggstart_time","href","info"],add_info(f1,{"diqu":w2}),f2]
            data.append(tmp)

    for w1 in ggtype.keys():
        for w2 in dztype.keys():
            p1="009002%s"%ggtype[w1]
            p2="009002%s%s"%(ggtype[w1],dztype[w2])
            href="http://www.lyggzyjy.cn/TPFront/jyxx/009002/%s/%s/?Paging=1"%(p1,p2)
            tmp=["zfcg_%s_diqu%s_gg"%(w1,dztype[w2]),href,["name","ggstart_time","href","info"],add_info(f1,{"diqu":w2}),f2]
            data.append(tmp)

    dztype1=OrderedDict([("市本级","001"),("涧西区","002"),("洛宁县","004"),("新安县","006")])

    for w in dztype1.keys():
        p2="009002004%s"%(dztype1[w])
        href="http://www.lyggzyjy.cn/TPFront/jyxx/009002/009002004/%s/?Paging=1"%(p2)
        tmp=["zfcg_gqita_diqu%s_gg"%(dztype1[w]),href,["name","ggstart_time","href","info"],add_info(f1,{"diqu":w}),f2]
        data.append(tmp)
    return data



data=get_data()


def work(conp,**args):
    est_meta(conp,data=data,diqu="河南省洛阳市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    work(conp=["postgres","since2015","192.168.4.175","henan","luoyang"])