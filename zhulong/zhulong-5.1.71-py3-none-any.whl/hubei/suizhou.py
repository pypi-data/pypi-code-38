import pandas as pd  
import re 

from selenium import webdriver 
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_query,db_command
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 

from zhulong.util.etl import est_meta,est_html,add_info
import time 
_name_="suizhou"

def f1(driver,num):
    locator=(By.ID,"listCon")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    val=driver.find_element_by_xpath("//div[@id='listCon']/ul/li[1]/a").text
    cnum=int(driver.find_element_by_xpath("//div[@class='pagination fr']//span[@class='page-cur']").text)
    if num!=cnum:

        driver.execute_script("SearchArticleOnce(643,0,%d,10)"%num)
        locator=(By.XPATH,"//div[@id='listCon']/ul/li[1]/a[string()!='%s']"%val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))



    page=driver.page_source

    soup=BeautifulSoup(page,"lxml")

    div=soup.find("div",id="listCon")
    ul=div.find("ul")
    lis=ul.find_all("li")
    data=[]
    for li in lis:
        span=li.find("span")
        a=li.find("a")
        tmp=[a["title"],"http://www.szztb.com.cn"+a["href"],span.text.strip()]
        data.append(tmp)
    df=pd.DataFrame(data)
    df["info"]=None
    return df 

def f2(driver):
    locator=(By.ID,"listCon")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    val=driver.find_element_by_xpath("//a[@class='page-end']").get_attribute("onclick")
    total=int(val.split(",")[2])
    driver.quit()
    return total

def f3(driver,url):


    driver.get(url)

    locator=(By.CLASS_NAME,"new_detail")

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

    soup=BeautifulSoup(page,'lxml')

    div=soup.find('div',class_='new_detail')
    #div=div.find_all('div',class_='ewb-article')[0]
    
    return div





data=[
    ["gcjs_gqita_zhao_zhong_gg","http://www.szztb.com.cn/Category/More?id=643&typeId=0",["name","href","ggstart_time","info"],f1,f2],

    ["zfcg_gqita_zhao_bian_zhong_liu_gg","http://www.szztb.com.cn/Category/More?id=644&typeId=0",["name","href","ggstart_time","info"],f1,f2],
    ]

def work(conp,**args):
    est_meta(conp,data,diqu="湖北省随州市",**args)
    est_html(conp,f=f3,**args)

if __name__=='__main__':
    work(conp=["postgres","since2015","127.0.0.1","hubei","suizhou"])