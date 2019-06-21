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

_name_="jiaozhuo"

# driver=webdriver.Chrome()

# url="http://www.jzggzy.cn/TPFront/ztbzx/069002/069002005/069002005004/MoreInfo.aspx?CategoryNum=69002005004"

# driver.get(url)

def f1(driver,num):
    locator=(By.XPATH,"//table[@id='MoreInfoList1_DataGrid1']//tr//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    #url=driver.current_url
    cnum=int(driver.find_element_by_xpath("//div[@id='MoreInfoList1_Pager']//font[@color='red']").text.strip())
    if num!=cnum:
        
        val=driver.find_element_by_xpath("//table[@id='MoreInfoList1_DataGrid1']//tr[1]//a").text.strip() 
        driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','%s')"%str(num))

        locator=(By.XPATH,"//table[@id='MoreInfoList1_DataGrid1']//tr[1]//a[not(contains(string(),'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


    page=driver.page_source

    soup=BeautifulSoup(page,"html.parser")

    div=soup.find("table",id="MoreInfoList1_DataGrid1")
    #ul=div.find("ul")
    trs=div.find_all("tr")

    data=[]

    for tr in trs:
        a=tr.find("a")
        ggstart_time=tr.find_all("td")[-1].text.strip()
        tmp=[a["title"].strip(),ggstart_time,"http://www.jzggzy.cn"+a["href"]]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 


def f2(driver):
    
    try:
        locator=(By.ID,"MoreInfoList1_Pager")
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

        total=driver.find_element_by_xpath("//div[@id='MoreInfoList1_Pager']/div[1]").text.strip()
        total=re.findall("总页数：([0-9]{1,})",total)[0]


        total=int(total)
    except:
        total=1
    driver.quit()
    return total



def f3(driver,url):


    driver.get(url)
    try:
        locator=(By.XPATH,"//div[contains(@id,'menutab')]")

        WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))
    except:
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

    if "tblInfo" in page:
        div=soup.find('table',id='tblInfo')
    else:
        div=soup.find("div",id=re.compile("menutab.*"),style="")
    #div=div.find_all('div',class_='ewb-article')[0]
    
    return div

data=[

        ["gcjs_zhaobiao_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002001/069002001001/MoreInfo.aspx?CategoryNum=69002001001",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_biangeng_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002001/069002001002/MoreInfo.aspx?CategoryNum=69002001002",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_kongzhijia_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002001/069002001003/MoreInfo.aspx?CategoryNum=69002001003",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_yucai_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002001/069002001004/MoreInfo.aspx?CategoryNum=69002001004",["name","ggstart_time","href","info"],f1,f2],


        ["gcjs_zhongbiaohx_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002001/069002001005/MoreInfo.aspx?CategoryNum=69002001005",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_yucai_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002002/069002002003/MoreInfo.aspx?CategoryNum=69002002003",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhaobiao_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002002/069002002001/MoreInfo.aspx?CategoryNum=69002002001",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_biangeng_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002002/069002002002/MoreInfo.aspx?CategoryNum=69002002002",["name","ggstart_time","href","info"],f1,f2],


        ["zfcg_zhongbiaohx_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002002/069002002004/MoreInfo.aspx?CategoryNum=69002002004",["name","ggstart_time","href","info"],f1,f2],

        ["yiliao_zhaobiao_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002005/069002005001/MoreInfo.aspx?CategoryNum=69002005001",["name","ggstart_time","href","info"],f1,f2],

        ["yiliao_biangeng_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002005/069002005002/MoreInfo.aspx?CategoryNum=69002005002",["name","ggstart_time","href","info"],f1,f2],

        #["yiliao_yucai_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002005/069002005003/MoreInfo.aspx?CategoryNum=69002005003",["name","ggstart_time","href","info"],f1,f2],

        ["yiliao_zhongbiaohx_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002005/069002005004/MoreInfo.aspx?CategoryNum=69002005004",["name","ggstart_time","href","info"],f1,f2],


    ]

def work(conp,**args):
    est_meta(conp,data=data,diqu="河南省焦作市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    work(conp=["postgres","since2015","127.0.0.1","henan","jiaozhuo"])