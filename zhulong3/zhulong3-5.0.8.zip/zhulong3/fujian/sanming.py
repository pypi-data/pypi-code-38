import time

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json

from zhulong3.util.etl import est_tbs, est_meta, est_html

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url = "http://www.smsjs.gov.cn/was5/web/search?channelid=212807&templet=docs.jsp&sortfield=-DOCORDERPRI,-docreltime&classsql=chnlid%3D8786&page=1&prepage=20"
# driver = webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_ = 'fujian_sanming'


def f1(driver, num):

    locator = (By.XPATH, '//body[string-length()>300]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url = driver.current_url
    cnum = re.findall('page=(\d+)&', url)[0]

    if cnum != str(num):
        length = len(driver.page_source)

        url = re.sub('page=\d+?&', 'page=%s&' % num, url)
        driver.get(url)

        WebDriverWait(driver, 10).until(
            lambda driver: len(driver.page_source) != length and len(driver.page_source) > 300)

    data = []
    html = driver.page_source

    content = re.findall('"docs":\[(.+)\]', html, re.S)[0]

    docs = re.findall('(?<!\<\!--){(.+?)}(?!--\>)', content, re.S)[:-1]
    for doc in docs:

        name = re.findall('"title":"(.+?)",', doc, re.S)[0]
        href = re.findall('"url":"(.+?)",', doc, re.S)[0]
        ggstart_time = re.findall('"time":"(.+?)",', doc, re.S)[0]
        tmp = [name, ggstart_time, href]
        # print(tmp)
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None

    return df


def f2(driver):
    locator = (By.XPATH, '//body[string-length()>300]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = re.findall('"pagenum":"(\d+?)",', driver.page_source)[0]
    total = int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//div[@class="box1 font1"]')

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    time.sleep(0.1)
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

    div = soup.find('div', class_='box1 font1').parent

    return div


data = [
    ["gcjs_zhaobiao_gg", "http://zjj.sm.gov.cn/was5/web/search?channelid=212807&templet=docs.jsp&sortfield=-DOCORDERPRI,-docreltime&classsql=chnlid%3D8786&page=1&prepage=20",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg", "http://zjj.sm.gov.cn/was5/web/search?channelid=212807&templet=docs.jsp&sortfield=-DOCORDERPRI,-docreltime&classsql=chnlid%3D8787&page=1&prepage=20",["name", "ggstart_time", "href", "info"], f1, f2],
]


##网址变更 http://zjj.sm.gov.cn
##变更时间 2019-5-22


def work(conp, **args):
    est_meta(conp, data=data, diqu="福建省三明市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "lch2", "fujian_sanming"]

    work(conp=conp,headless=False,num=1)
    pass