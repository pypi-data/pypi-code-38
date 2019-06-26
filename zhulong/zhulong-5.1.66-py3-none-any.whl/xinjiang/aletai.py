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

from zhulong.util.etl import est_html, est_meta, add_info

_name_ = "aletai"


def f1(driver, num):

    locator = (By.XPATH, '//div[@class="ewb-infoList"]//li[1]/a')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    url=driver.current_url
    cnum=re.findall('pageing=(\d+)',url)[0]

    if num != int(cnum):
        val = driver.find_element_by_xpath('//div[@class="ewb-infoList"]//li[1]/a').get_attribute('href')[-40:-10]
        url=re.sub('(?<=pageing=)\d+',str(num),url)
        driver.get(url)
        locator = (By.XPATH, "//div[@class='ewb-infoList']//li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    tbody = soup.find("div", class_='ewb-infoList')
    trs = tbody.find_all("li")
    data = []
    for tr in trs:
        href= tr.find("a")['href']
        name= tr.find("a").get_text().strip()
        if not name:
            name='空'
        ggstart_time=tr.find('span').get_text().strip()
        if 'http' in href:
            href = href
        else:
            href = 'http://www.xjaltggzy.gov.cn' +href

        tmp = [name,ggstart_time,href]

        data.append(tmp)
    df = pd.DataFrame(data)
    df['info']=None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="ewb-infoList"]//li[1]/a')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    try:
        total=driver.find_element_by_xpath('//div[@class="paging"]//li[last()-3]/a').text
        total=re.findall('/(\d+)',total)[0]
    except:
        total=1
    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="article-block"][string-length()>50]')
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))

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
    div = soup.find('div', class_='article-block')
    return div


data = [
    ["gcjs_zhaobiao_gg","http://www.xjaltggzy.gov.cn/TPFront/jyfu/011001/011001001/?pageing=2",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg","http://www.xjaltggzy.gov.cn/TPFront/jyfu/011001/011001002/?pageing=2",["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_xunjia_gg","http://www.xjaltggzy.gov.cn/TPFront/xwdt/010001/?pageing=1",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"询价采购"}), f2],
    ["zfcg_zhaobiao_gg","http://www.xjaltggzy.gov.cn/TPFront/xwdt/010002/?pageing=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg","http://www.xjaltggzy.gov.cn/TPFront/xwdt/010003/?pageing=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_gqita_da_bian_gg","http://www.xjaltggzy.gov.cn/TPFront/xwdt/010004/?pageing=1",["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_shuili_gg","http://www.xjaltggzy.gov.cn/TPFront/sljt/022001/022001001/?pageing=1",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"水利工程"}), f2],
    ["gcjs_biangeng_shuili_gg","http://www.xjaltggzy.gov.cn/TPFront/sljt/022001/022001003/?pageing=1",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"水利工程"}), f2],
    ["gcjs_zhongbiao_shuili_gg","http://www.xjaltggzy.gov.cn/TPFront/sljt/022001/022001002/?pageing=1",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"水利工程"}), f2],

    ["gcjs_zhaobiao_jiaotong_gg","http://www.xjaltggzy.gov.cn/TPFront/sljt/022002/022002001/?pageing=1",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"交通工程"}), f2],
    ["gcjs_biangeng_jiaotong_gg","http://www.xjaltggzy.gov.cn/TPFront/sljt/022002/022002003/?pageing=1",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"交通工程"}), f2],
    ["gcjs_zhongbiao_jiaotong_gg","http://www.xjaltggzy.gov.cn/TPFront/sljt/022002/022002002/?pageing=1",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"交通工程"}), f2],

    ["gcjs_zhaobiao_nongtian_gg","http://www.xjaltggzy.gov.cn/TPFront/sljt/022003/022003001/?pageing=1",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"高标准农田"}), f2],
    ["gcjs_biangeng_nongtian_gg","http://www.xjaltggzy.gov.cn/TPFront/sljt/022003/022003003/?pageing=1",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"高标准农田"}), f2],
    ["gcjs_zhongbiao_nongtian_gg","http://www.xjaltggzy.gov.cn/TPFront/sljt/022003/022003002/?pageing=1",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"高标准农田"}), f2],


]


def work(conp, **args):
    est_meta(conp, data=data,pageloadtimeout=120,pageLoadStrategy='none', diqu="新疆省阿勒泰市", **args)
    est_html(conp, f=f3,pageloadtimeout=60, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "xinjiang", "aletai"],num=1,headless=False)

