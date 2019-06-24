import math
import random

import pandas as pd
import re

import requests
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time

from zhulong2.util.etl import est_html, est_meta, add_info, est_meta_large

_name_ = "chongqing_chongqing"


def f1(driver, num):
    locator = (By.XPATH, "//body/pre[string-length()>100][contains(string(),'success')]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=re.findall('pi=(\d+)&',url)[0]

    if num != int(cnum):
        val1=driver.find_element_by_xpath('//body/pre').text[10:60]
        val = len(driver.page_source)
        url=re.sub('(?<=pi=)\d+',str(num),url)

        driver.get(url)
        locator = (By.XPATH, "//body/pre[string-length()>100][not(contains(string(), '%s'))]" % val1)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        WebDriverWait(driver, 10).until(lambda driver:len(driver.page_source) != val)
    data = []
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    content = soup.find("pre").get_text()
    content=json.loads(content)
    contents=content['notices']
    for c in contents:
        name=c.get('title')
        daili=c.get('creatorOrgName')
        diqu=c.get('districtName')
        proname=c.get('projectDirectoryName')
        buyer=c.get('buyerName')
        ggstart_time=c.get('bidBeginTime')
        mark_id=c.get('id')
        href='https://www.cqgp.gov.cn/notices/detail/{mark_id}?title={title}'.format(mark_id=mark_id,title=name)
        info=json.dumps({"daili":daili,"diqu":diqu,"proname":proname,"buyer":buyer},ensure_ascii=False)

        tmp = [name, ggstart_time, href,info]

        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.XPATH, "//body/pre[string-length()>100][contains(string(),'success')]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    html=driver.page_source

    total=re.findall('"total":(\d+)',html)[0]
    total=math.ceil(int(total)/20)
    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@id="notice"][string-length()>50]')
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 5: break
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div',id='notice')

    return div


data = [
    ["zfcg_gqita_caigou_gg",
     "https://www.cqgp.gov.cn/gwebsite/api/v1/notices/stable?pi=1&ps=20&type=100,200,201,202,203,204,205,206,300,301,302,303,304,3041,305,400,401,4001&userType=41,42",
     ["name", "ggstart_time", "href", "info"], f1, f2],

 ["zfcg_gqita_jizhongcaigou_gg",
     "https://www.cqgp.gov.cn/gwebsite/api/v1/notices/stable?pi=1&ps=20&type=100,200,201,202,203,204,205,206,300,301,302,303,304,3041,305,400,401,4001&userType=32,34",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"集中采购"}), f2],

 ["zfcg_gqita_daili_gg",
     "https://www.cqgp.gov.cn/gwebsite/api/v1/notices/stable?pi=1&ps=20&type=100,200,201,202,203,204,205,206,300,301,302,303,304,3041,305,400,401,4001&userType=43",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"代理机构"}), f2],

 ["zfcg_gqita_fensan_gg",
     "https://www.cqgp.gov.cn/gwebsite/api/v1/notices/stable?pi=2&ps=20&type=207,306,307,308,309,402,3091",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"分散采购"}), f2],

 ["zfcg_gqita_jingjia_gg",
     "https://www.cqgp.gov.cn/gwebsite/api/v1/notices/stable?pi=2&projectPurchaseWay=6003,6001&ps=20&type=100,200,201,202,203,204,205,206,300,301,302,303,304,3041,305,400,401,4001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"网上交易"}), f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data,interval_page=2000,num=20, diqu="重庆市", **args)
    est_html(conp, f=f3, **args)



if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch", "chongqing"],headless=True,num=1,total=3)
