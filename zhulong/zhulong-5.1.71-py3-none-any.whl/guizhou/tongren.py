
# coding=utf-8

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
from zhulong.util.etl import gg_meta,gg_html,est_meta,est_html,est_tbs

_name_="tongren"

def f1(driver,num):

    locator=(By.XPATH,'//td[@id="tdcontent"]//tr[1]//a')
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum = int(re.findall('Paging=(\d+)',url)[0])
    if cnum != num:
        val=driver.find_element_by_xpath('//td[@id="tdcontent"]//tr[1]//a').get_attribute('href')[-30:]
        url=re.sub('Paging=\d+','Paging=%s'%num,url)
        driver.get(url)
        locator=(By.XPATH,'//td[@id="tdcontent"]//tr[1]//a[not(contains(@href,"%s"))]'%val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page=driver.page_source
    soup=BeautifulSoup(page,"html.parser")
    tb=soup.find('td',id="tdcontent")
    trs=tb.find_all("tr")
    data=[]
    for tr in trs:

        name=tr.find('td',align="left").a['title']
        href=tr.find('td',align="left").a['href']
        ggstart_time=tr.find('td',align="right").get_text().strip()
        diqu=tr.find('td',align="left").font.get_text()
        info=json.dumps({'diqu':diqu},ensure_ascii=False)

        if 'http' in href:
            href=href
        else:
            href='http://www.trjyzx.cn'+href

        tmp=[name,href,ggstart_time,info]
        data.append(tmp)
    df=pd.DataFrame(data=data)

    return df

def f4(driver,num):

    locator=(By.XPATH,'//div[@class="menu-info-bd"]/div[1]/table//tr[1]//a')
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum = int(re.findall('Paging=(\d+)',url)[0])
    if cnum != num:
        val=driver.find_element_by_xpath('//div[@class="menu-info-bd"]/div[1]/table//tr[1]//a').get_attribute('href')[-30:]
        url=re.sub('Paging=\d+','Paging=%s'%num,url)
        driver.get(url)
        locator=(By.XPATH,'//div[@class="menu-info-bd"]/div[1]/table//tr[1]//a[not(contains(@href,"%s"))]'%val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page=driver.page_source
    soup=BeautifulSoup(page,"html.parser")
    tb=soup.find('div',class_="menu-info-bd").find('div')
    trs=tb.find_all("tr")
    data=[]
    for tr in trs:

        name=tr.find('td',align="left").a['title']
        href=tr.find('td',align="left").a['href']
        ggstart_time=tr.find('td',align="right").get_text().strip()
        diqu=tr.find('td',align="left").font.get_text()
        info=json.dumps({'diqu':diqu},ensure_ascii=False)

        if 'http' in href:
            href=href
        else:
            href='http://www.trjyzx.cn'+href

        tmp=[name,href,ggstart_time,info]
        data.append(tmp)
    df=pd.DataFrame(data=data)

    return df




def f2(driver):
    locator=(By.XPATH,'//td[@id="tdcontent"]//tr[1]//a | //div[@class="menu-info-bd"]/div[1]/table//tr[1]//a')
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    atext=driver.find_element_by_xpath('//td[@class="huifont"]').text

    total=int(atext.split("/")[1])

    driver.quit()

    return total

def f3(driver,url):

    driver.get(url)

    locator=(By.XPATH,'//table[@id="tblInfo"][string-length()>50]')

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

    div=soup.find('table',id="tblInfo")

    return div


data=[
    ["gcjs_zhaobiao_gg","http://www.trjyzx.cn/TPFront_TR/showinfo/Moreggxxlist.aspx?CategoryNum=002001001&Paging=1",["name","href","ggstart_time","info"],f1,f2],

    ["gcjs_biangeng_gg","http://www.trjyzx.cn/TPFront_TR/jyzx/002001/002001003/?Paging=1",["name","href","ggstart_time","info"],f4,f2],

    ["gcjs_zhongbiao_gg","http://www.trjyzx.cn/TPFront_TR/jyzx/002001/002001002/?Paging=1",["name","href","ggstart_time","info"],f4,f2],

    ["gcjs_liubiao_gg","http://www.trjyzx.cn/TPFront_TR/jyzx/002001/002001004/?Paging=1",["name","href","ggstart_time","info"],f4,f2],

    ["zfcg_yucai_gg","http://www.trjyzx.cn/TPFront_TR/jyzx/002002/002002005/?Paging=1",["name","href","ggstart_time","info"],f4,f2],

    ["zfcg_zhaobiao_gg","http://www.trjyzx.cn/TPFront_TR/showinfo/Moreggxxlist.aspx?CategoryNum=002002001&Paging=1",["name","href","ggstart_time","info"],f1,f2],

    ["zfcg_zhongbiao_gg","http://www.trjyzx.cn/TPFront_TR/jyzx/002002/002002002/?Paging=1",["name","href","ggstart_time","info"],f4,f2],

    ["gcjs_biangeng_gg","http://www.trjyzx.cn/TPFront_TR/jyzx/002002/002002003/?Paging=1",["name","href","ggstart_time","info"],f4,f2],

    ["zfcg_liubiao_gg","http://www.trjyzx.cn/TPFront_TR/jyzx/002002/002002004/?Paging=1",["name","href","ggstart_time","info"],f4,f2]

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="贵州省同仁市",**args)

    est_html(conp,f=f3,**args)


if __name__ == '__main__':

    work(conp=["postgres","since2015","192.168.3.171","guizhou","tongren"],pageloadstrategy='none',total=10)