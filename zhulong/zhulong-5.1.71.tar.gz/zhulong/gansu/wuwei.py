import pandas as pd  
import re

import requests
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
from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, add_info
from zhulong.util.fake_useragent import UserAgent

_name_="wuwei"

# driver=webdriver.Chrome()

# url="http://www.wwggzy.com/f/trade/annogoods/list?tradeStatus=1&selectedProjectType=2"

# driver.get(url)


def f1(driver,num):
    
    locator=(By.XPATH,'//dl[@class="byTradingDetailParent clear"][1]//a')
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//li[@class="paginate_button active"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum=int(driver.find_element_by_xpath("//li[@class='paginate_button active']/a").text)

    if num!=cnum:
        page_count = len(driver.page_source)
        val=driver.find_element_by_xpath('//dl[@class="byTradingDetailParent clear"][1]//a').get_attribute('href')[-20:-5]
        driver.execute_script("page(%d,20,'');"%num)

        locator=(By.XPATH,"//dl[@class='byTradingDetailParent clear'][1]//a[not(contains(@href,'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
        WebDriverWait(driver, 10).until(lambda driver: len(driver.page_source) != page_count)

    page=driver.page_source

    soup=BeautifulSoup(page,"html.parser")

    dls=soup.find_all("dl",class_="byTradingDetailParent clear")

    data=[]

    for dl in dls:
        a=dl.find("a")
        name=a.get_text().strip()
        href=a['href']
        href='http://www.wwggzy.com'+href
        ggstart_time=dl.find("span",class_='byTradingDetailTime').get_text()
        tmp=[name,ggstart_time,href]
        # print(tmp)
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 


def f2(driver):

    locator=(By.XPATH,'//dl[@class="byTradingDetailParent clear"][1]//a')
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    locator=(By.XPATH,'//li[@class="paginate_button active"]')
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    try:
        total=driver.find_element_by_xpath("//ul[@class='pagination pagination-outline']/li[last()-2]").text
        total=int(total)
    except:
        total=1
    driver.quit()
    return total


def f4(driver,num):
    proxies_data = webdriver.DesiredCapabilities.CHROME
    proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
    if proxies_chromeOptions:
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    else:
        proxies = {}

    ua=UserAgent()

    url_list=driver.current_url.split('?lch?')
    req_url=url_list[0]
    procode=url_list[1].split('=')[1]
    tabletype=url_list[2].split('=')[1]

    form_data = {
            "pageNo": num,
            "pageSize": 20,
            "tradeStatus": 1,
            "prjpropertycode": procode,
            "projectname": None,
            "tabType": tabletype,

            }

    headers = {
        "Referer": "http://www.wwggzy.com/f/trade/annogoods/list?tradeStatus=1",
        "User-Agent": ua.chrome}

    req = requests.post(req_url, data=form_data, headers=headers,proxies=proxies, timeout=20)
    if req.status_code != 200:
        raise ValueError('response status_code is %s'%req.status_code)

    soup = BeautifulSoup(req.text, 'html.parser')
    dls = soup.find_all("dl", class_="byTradingDetailParent clear")

    data = []

    for dl in dls:
        a = dl.find("a")
        name = a.get_text().strip()
        href = a['href']
        href='http://www.wwggzy.com'+href
        ggstart_time = dl.find("span", class_='byTradingDetailTime').get_text()
        tmp = [name, ggstart_time, href]
        # print(tmp)
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df

def f5(driver):
    proxies_data = webdriver.DesiredCapabilities.CHROME
    proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
    if proxies_chromeOptions:
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    else:
        proxies = {}

    ua = UserAgent()
    url_list = driver.current_url.split('?lch?')
    req_url = url_list[0]
    procode = url_list[1].split('=')[1]
    tabletype = url_list[2].split('=')[1]

    form_data = {
        "pageNo": 1,
        "pageSize": 20,
        "tradeStatus": 1,
        "prjpropertycode": procode,
        "projectname": None,
        "tabType": tabletype,
    }

    headers = {
        "Referer": "http://www.wwggzy.com/f/trade/annogoods/list?tradeStatus=1",
        "User-Agent": ua.chrome}

    req = requests.post(req_url, data=form_data, headers=headers, proxies=proxies,timeout=20)
    if req.status_code != 200:
        raise ValueError('response status_code is %s' % req.status_code)

    soup = BeautifulSoup(req.text, 'html.parser')

    total = soup.find_all('li', class_='paginate_button ')
    if total:
        total = int(total[-1].get_text())
    else:
        total = 1

    driver.quit()
    return total



def f3(driver,url):


    driver.get(url)

    locator=(By.XPATH,'//div[@id="content"][string-length()>100] | //div[@class="jxTradingMainLayer clear"][string-length()>50]')

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

    div=soup.find('div',id='content')
    if div == None:
        div=soup.find('div',class_='jxTradingMainLayer clear')

    return div



data=[

    ###新系统

        ["gcjs_zhaobiao_gg","http://www.wwggzy.com/f/newtrade/annogoods/list?index=1&selectedProjectType=A01,A02,A99",["name","ggstart_time","href","info"],f1,f2],
        ["gcjs_zhongbiao_gg","http://www.wwggzy.com/f/newtrade/annogoods/list?index=2&selectedProjectType=A01,A02,A99",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhaobiao_jiaotong_gg","http://www.wwggzy.com/f/newtrade/annogoods/list?index=1&selectedProjectType=A03",["name","ggstart_time","href","info"],add_info(f1,{"gclx":"交通工程"}),f2],
        ["gcjs_zhongbiao_jiaotong_gg","http://www.wwggzy.com/f/newtrade/annogoods/list?index=2&selectedProjectType=A03",["name","ggstart_time","href","info"],add_info(f1,{"gclx":"交通工程"}),f2],

        ["gcjs_zhaobiao_shuili_gg","http://www.wwggzy.com/f/newtrade/annogoods/list?index=1&selectedProjectType=A07",["name","ggstart_time","href","info"],add_info(f1,{"gclx":"水利工程"}),f2],
        ["gcjs_zhongbiao_shuili_gg","http://www.wwggzy.com/f/newtrade/annogoods/list?index=2&selectedProjectType=A07",["name","ggstart_time","href","info"],add_info(f1,{"gclx":"水利工程"}),f2],

        ["gcjs_zhaobiao_xiane_gg","http://www.wwggzy.com/f/newtrade/annogoods/list?index=1&selectedProjectType=801",["name","ggstart_time","href","info"],add_info(f1,{"gclx":"限额以下"}),f2],
        ["gcjs_zhongbiao_xiane_gg","http://www.wwggzy.com/f/newtrade/annogoods/list?index=2&selectedProjectType=801",["name","ggstart_time","href","info"],add_info(f1,{"gclx":"限额以下"}),f2],

        ["zfcg_zhaobiao_xiane_gg","http://www.wwggzy.com/f/newtrade/annogoods/list?index=1&selectedProjectType=802",["name","ggstart_time","href","info"],add_info(f1,{"gclx":"限额以下"}),f2],
        ["zfcg_zhongbiao_xiane_gg","http://www.wwggzy.com/f/newtrade/annogoods/list?index=2&selectedProjectType=802",["name","ggstart_time","href","info"],add_info(f1,{"gclx":"限额以下"}),f2],

        ["zfcg_zhaobiao_xieyi_gg","http://www.wwggzy.com/f/newtrade/annogoods/list?index=1&selectedProjectType=800",["name","ggstart_time","href","info"],add_info(f1,{"gclx":"协议供货"}),f2],
        ["zfcg_zhongbiao_xieyi_gg","http://www.wwggzy.com/f/newtrade/annogoods/list?index=2&selectedProjectType=800",["name","ggstart_time","href","info"],add_info(f1,{"gclx":"协议供货"}),f2],

        ["zfcg_zhaobiao_gg","http://www.wwggzy.com/f/newtrade/annogoods/list?index=1&selectedProjectType=D01,D02,D03",["name","ggstart_time","href","info"],f1,f2],
        ["zfcg_zhongbiao_gg","http://www.wwggzy.com/f/newtrade/annogoods/list?index=2&selectedProjectType=D01,D02,D03",["name","ggstart_time","href","info"],f1,f2],

    ##旧系统
    ["gcjs_zhaobiao_old_gg","http://www.wwggzy.com/f/trade/annogoods/getAnnoList?lch?procode=A?lch?tabletype=1",["name","ggstart_time","href","info"],f4,f5],
    ["gcjs_zhongbiao_old_gg","http://www.wwggzy.com/f/trade/annogoods/getAnnoList?lch?procode=A?lch?tabletype=2",["name","ggstart_time","href","info"],f4,f5],

    ["gcjs_zhaobiao_jiaotong_old_gg","http://www.wwggzy.com/f/trade/annogoods/getAnnoList?lch?procode=A02?lch?tabletype=1",["name","ggstart_time","href","info"],add_info(f4,{"gclx":"交通工程"}),f5],
    ["gcjs_zhongbiao_jiaotong_old_gg","http://www.wwggzy.com/f/trade/annogoods/getAnnoList?lch?procode=A02?lch?tabletype=2",["name","ggstart_time","href","info"],add_info(f1,{"gclx":"交通工程"}),f5],

    ["gcjs_zhaobiao_shuili_old_gg","http://www.wwggzy.com/f/trade/annogoods/getAnnoList?lch?procode=A03?lch?tabletype=1",["name","ggstart_time","href","info"],add_info(f4,{"gclx":"水利工程"}),f5],
    ["gcjs_zhongbiao_shuili_old_gg","http://www.wwggzy.com/f/trade/annogoods/getAnnoList?lch?procode=A03?lch?tabletype=2",["name","ggstart_time","href","info"],add_info(f4,{"gclx":"水利工程"}),f5],

    ["zfcg_zhaobiao_old_gg","http://www.wwggzy.com/f/trade/annogoods/getAnnoList?lch?procode=D?lch?tabletype=1",["name","ggstart_time","href","info"],f4,f5],
    ["zfcg_zhongbiao_old_gg","http://www.wwggzy.com/f/trade/annogoods/getAnnoList?lch?procode=D?lch?tabletype=2",["name","ggstart_time","href","info"],f4,f5],

]


## f3 是全流程

def work(conp,**args):
    est_meta(conp,data=data,diqu="甘肃省武威市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    work(conp=["postgres","since2015",'192.168.3.171',"gansu","wuwei"],headless=False,num=1)