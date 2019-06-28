
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


_name_="shenghui"

def f1(driver,num):

    locator=(By.XPATH,'//ul[@id="news_list1"]/li[1]/a')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum = int(re.findall('queryContent_(\d+)\.jspx',url)[0])

    if cnum != num:
        val=driver.find_element_by_xpath('//ul[@id="news_list1"]/li[1]/a').get_attribute('href')

        url=re.sub("queryContent_\d+\.jspx","queryContent_%s.jspx"%num,url)
        driver.get(url)
        locator=(By.XPATH,"//ul[@id='news_list1']/li[1]/a[not(contains(@href,'%s'))]"%val)
        WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))

    page=driver.page_source
    soup=BeautifulSoup(page,"html.parser")
    ul=soup.find('ul',id="news_list1")
    lis=ul.find_all("li")
    data=[]
    for li in lis:
        name=li.a['title']
        href=li.a['href']
        ggstart_time=li.find('span',class_='times').get_text().strip()
        diqu=li.a.span.get_text().strip()

        if 'http' in href:
            href=href
        else:
            href='http://www.gzjyfw.gov.cn'+ href
        info=json.dumps({'diqu':diqu},ensure_ascii=False)
        tmp=[name,href,ggstart_time,info]

        data.append(tmp)
    df=pd.DataFrame(data=data)

    return df

def f2(driver):
    locator=(By.XPATH,'//ul[@id="news_list1"]/li[1]/a')
    WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))

    html=driver.page_source
    total=re.findall('<li><a href="###">共\d+条记录 1/(\d+)页</a></li>',html)[0]

    driver.quit()

    return int(total)


def f3(driver,url):

    driver.get(url)

    locator=(By.XPATH,'//div[@class="content_box"][string-length()>100]')

    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

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

    div=soup.find('div',class_='content_box')
    return div

data=[
["gcjs_zhaobiao_gg","http://www.gzjyfw.gov.cn/gcms/queryContent_1.jspx?title=&businessCatalog=CE&businessType=JYGG&inDates=800&ext=&origin=ALL",["name","href","ggstart_time","info"],f1,f2],

["gcjs_zgys_gg","http://www.gzjyfw.gov.cn/gcms/queryContent_1.jspx?title=&businessCatalog=CE&businessType=ZSJGGS&inDates=800&ext=&origin=ALL",["name","href","ggstart_time","info"],f1,f2],

["gcjs_zhongbiao_gg","http://www.gzjyfw.gov.cn/gcms/queryContent_1.jspx?title=&businessCatalog=CE&businessType=JYJGGS&inDates=800&ext=&origin=ALL",["name","href","ggstart_time","info"],f1,f2],

["gcjs_liubiao_gg","http://www.gzjyfw.gov.cn/gcms/queryContent_1.jspx?title=&businessCatalog=CE&businessType=FBGG&inDates=800&ext=&origin=ALL",["name","href","ggstart_time","info"],f1,f2],

["zfcg_zhaobiao_gg","http://www.gzjyfw.gov.cn/gcms/queryContent_1.jspx?title=&businessCatalog=GP&businessType=JYGG&inDates=800&ext=&origin=ALL",["name","href","ggstart_time","info"],f1,f2],

["zfcg_zgys_gg","http://www.gzjyfw.gov.cn/gcms/queryContent_1.jspx?title=&businessCatalog=GP&businessType=ZSJGGS&inDates=800&ext=&origin=ALL",["name","href","ggstart_time","info"],f1,f2],

["zfcg_zhongbiao_gg","http://www.gzjyfw.gov.cn/gcms/queryContent_1.jspx?title=&businessCatalog=GP&businessType=JYJGGS&inDates=800&ext=&origin=ALL",["name","href","ggstart_time","info"],f1,f2],

["zfcg_liubiao_gg","http://www.gzjyfw.gov.cn/gcms/queryContent_1.jspx?title=&businessCatalog=GP&businessType=FBGG&inDates=800&ext=&origin=ALL",["name","href","ggstart_time","info"],f1,f2],

["qsy_zhaobiao_gg","http://www.gzjyfw.gov.cn/gcms/queryContent_1.jspx?title=&businessCatalog=GQZB&businessType=JYGG&inDates=800&ext=&origin=ALL",["name","href","ggstart_time","info"],f1,f2],


]

def work(conp,**args):
    est_meta(conp,data=data,diqu="贵州省省会",**args)

    est_html(conp,f=f3,**args)
if __name__ == '__main__':

    work(conp=["postgres","since2015","192.168.3.171","guizhou","shenghui"],headless=False,num=1)