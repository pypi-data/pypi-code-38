
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


_name_="bijie"
def f1(driver,num):
    locator = (By.XPATH, '//div[@class="list_main_right_content"]//li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    if 'index.shtml' in url:
        cnum=1
    else:
        cnum=int(re.findall('index_(\d+).shtml',url)[0])
    if cnum != num:
        val=driver.find_element_by_xpath('//div[@class="list_main_right_content"]//li[1]//a').get_attribute('href')[-20:-5]

        if num ==1:
            url = re.sub("index_\d+.shtml", "index.shtml", url)
        else:
            url = re.sub("index_\d+.shtml", "index_%d.shtml" % num, url)

        driver.get(url)
        locator=(By.XPATH,'//div[@class="list_main_right_content"]//li[1]//a[not(contains(@href,"%s"))]'%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    page=driver.page_source
    soup=BeautifulSoup(page,"html.parser")

    lis=soup.find('div',class_='list_main_right_content').find_all('li')

    data=[]
    for li in lis:
        name=li.find("a")['title']
        href=li.find("a")['href']
        ggstart_time=li.find("span").get_text()
        if 'http' in href:
            href=href
        else:
            href='http://www.bijie.gov.cn'+href

        tmp=[name,href,ggstart_time]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df

def f2(driver):
    locator = (By.XPATH, '//div[@class="list_main_right_content"]//li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        total=driver.find_element_by_xpath('//div[@class="pager_num"]//span[1]').text
        total=int(re.findall('/(\d+)',total)[0])
    except:
        total=1
    driver.quit()

    return total
def f3(driver,url):

    driver.get(url)

    locator=(By.XPATH,'//div[@class="detail_main"][string-length()>100]')

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

    div=soup.find('div',class_='detail_main')
    return div

data=[
["gcjs_zhaobiao_gg","http://www.bijie.gov.cn/bm/bjsggzyjyzx/jy/jsgc/zbgg/index_2.shtml",["name","href","ggstart_time","info"],f1,f2],
["gcjs_dayi_gg","http://www.bijie.gov.cn/bm/bjsggzyjyzx/jy/jsgc/cqgg/index_2.shtml",["name","href","ggstart_time","info"],f1,f2],

["gcjs_biangeng_gg","http://www.bijie.gov.cn/bm/bjsggzyjyzx/jy/jsgc/bggg/index_2.shtml",["name","href","ggstart_time","info"],f1,f2],

["gcjs_zhongbiaohx_gg","http://www.bijie.gov.cn/bm/bjsggzyjyzx/jy/jsgc/zbgs/index_2.shtml",["name","href","ggstart_time","info"],f1,f2],

["gcjs_liubiao_gg","http://www.bijie.gov.cn/bm/bjsggzyjyzx/jy/jsgc/lbgg/index_2.shtml",["name","href","ggstart_time","info"],f1,f2],

["zfcg_zhaobiao_gg","http://www.bijie.gov.cn/bm/bjsggzyjyzx/jy/zfcg/cggg/index_2.shtml",["name","href","ggstart_time","info"],f1,f2],
["zfcg_dayi_gg","http://www.bijie.gov.cn/bm/bjsggzyjyzx/jy/zfcg/cqgg/index_2.shtml",["name","href","ggstart_time","info"],f1,f2],

["zfcg_biangeng_gg","http://www.bijie.gov.cn/bm/bjsggzyjyzx/jy/zfcg/bggg/index_2.shtml",["name","href","ggstart_time","info"],f1,f2],

["zfcg_zhongbiao_gg","http://www.bijie.gov.cn/bm/bjsggzyjyzx/jy/zfcg/jggg/index_2.shtml",["name","href","ggstart_time","info"],f1,f2],

["zfcg_liubiao_gg","http://www.bijie.gov.cn/bm/bjsggzyjyzx/jy/zfcg/lbgg/index_2.shtml",["name","href","ggstart_time","info"],f1,f2]

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="贵州省毕节市",**args)

    est_html(conp,f=f3,**args)
if __name__ == '__main__':

    work(conp=["postgres","since2015","192.168.3.171","guizhou","bijie"],pageloadstrategy='none')