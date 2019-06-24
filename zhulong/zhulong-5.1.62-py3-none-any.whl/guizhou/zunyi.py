
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


_name_="zunyi"

def f1(driver,num):
    locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url=driver.current_url

    cnum=re.findall('Paging=(\d+)',url)[0]

    if int(cnum) != num:
        val=driver.find_element_by_xpath('//ul[@class="wb-data-item"]/li[1]//a').get_attribute('href')[-50:-15]

        url = re.sub("Paging=[0-9]*", "Paging=%s" % num, url)
        driver.get(url)
        locator=(By.XPATH,'//ul[@class="wb-data-item"]/li[1]//a[not(contains(@href,"%s"))]'%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    page=driver.page_source
    soup=BeautifulSoup(page,"html.parser")
    ul=soup.find("ul",class_="wb-data-item")
    lis=ul.find_all("li")
    data=[]
    for li in lis:
        a=li.find("a")
        href=a['href']
        name=a['title']
        ggstart_time=li.find("span",class_="wb-data-date").text

        href='http://ggzyjy.zunyi.gov.cn'+href
        tmp=[name,href,ggstart_time]

        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df


def f2(driver):
    locator=(By.XPATH,'//ul[@class="wb-data-item"]/li[1]//a')
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    ttext=driver.find_element_by_xpath('//td[@class="huifont"]').text
    total=int(ttext.split("/")[1])

    driver.quit()

    return total



def f3(driver,url):

    driver.get(url)

    locator=(By.XPATH,'//div[@class="detail-info"][string-length()>50]')

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

    div=soup.find('div',class_='detail-info')
    return div



data=[
    ["gcjs_zhaobiao_gg","http://ggzyjy.zunyi.gov.cn/index/jyxx/013001/013001001/?Paging=1",["name","href","ggstart_time","info"],f1,f2],
    ["gcjs_biangeng_gg","http://ggzyjy.zunyi.gov.cn/index/jyxx/013001/013001002/?Paging=1",["name","href","ggstart_time","info"],f1,f2],
    ["gcjs_gqita_da_bian_gg","http://ggzyjy.zunyi.gov.cn/index/jyxx/013001/013001006/?Paging=1",["name","href","ggstart_time","info"],f1,f2],
    ["gcjs_zhongbiaohx_gg","http://ggzyjy.zunyi.gov.cn/index/jyxx/013001/013001003/?Paging=1",["name","href","ggstart_time","info"],f1,f2],
    ["gcjs_zhongbiao_gg","http://ggzyjy.zunyi.gov.cn/index/jyxx/013001/013001007/?Paging=1",["name","href","ggstart_time","info"],f1,f2],
    ["gcjs_liubiao_gg","http://ggzyjy.zunyi.gov.cn/index/jyxx/013001/013001005/?Paging=1",["name","href","ggstart_time","info"],f1,f2],


    ["zfcg_zhaobiao_gg","http://ggzyjy.zunyi.gov.cn/index/jyxx/013002/013002001/?Paging=1",["name","href","ggstart_time","info"],f1,f2],
    ["zfcg_biangeng_gg","http://ggzyjy.zunyi.gov.cn/index/jyxx/013002/013002002/?Paging=1",["name","href","ggstart_time","info"],f1,f2],
    ["zfcg_zhongbiao_gg","http://ggzyjy.zunyi.gov.cn/index/jyxx/013002/013002004/?Paging=1",["name","href","ggstart_time","info"],f1,f2],
    ["zfcg_liubiao_gg","http://ggzyjy.zunyi.gov.cn/index/jyxx/013002/013002003/?Paging=1",["name","href","ggstart_time","info"],f1,f2],
    ["zfcg_zgys_gg","http://ggzyjy.zunyi.gov.cn/index/jyxx/013002/013002005/?Paging=1",["name","href","ggstart_time","info"],f1,f2],
    ["zfcg_zgysjg_gg","http://ggzyjy.zunyi.gov.cn/index/jyxx/013002/013002006/?Paging=1",["name","href","ggstart_time","info"],f1,f2]

]



def work(conp,**args):
    est_meta(conp,data=data,diqu="贵州省遵义市",**args)

    est_html(conp,f=f3,**args)

if __name__ == '__main__':

    work(conp=["postgres","since2015","192.168.3.171","guizhou","zunyi"],num=1)