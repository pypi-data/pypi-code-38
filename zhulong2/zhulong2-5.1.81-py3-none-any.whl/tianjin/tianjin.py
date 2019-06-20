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

_name_ = "tianjin_tianjin"


def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='dataList']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//span[@class='selectPage']")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = re.findall(r'(\d+)', cnum)[0]
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='dataList']/li[1]/a").get_attribute('href')[-16:]
        driver.execute_script('findGoodsAndRef({},1);'.format(num))
        locator = (By.XPATH, "//ul[@class='dataList']/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    tbody = soup.find("ul", class_='dataList')
    trs = tbody.find_all("li")
    data = []
    for tr in trs:
        a = tr.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        href = a['href'].strip()
        if 'http' in href:
            link = href
        else:
            link = 'http://www.ccgp-tianjin.gov.cn/portal/documentView.do?method=view&' + href.split('?', maxsplit=1)[1]
        span = tr.find('span', class_='time').text.strip()
        tmp = [title, span, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//ul[@class='dataList']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//span[@class='countPage']/b")
        num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//td[@valign='top'][string-length()>10]")
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
    div = soup.find('td', attrs={'valign': 'top', 'bgcolor': '#ffffff'})
    return div


data = [
    ["zfcg_yucai_shiji_gg",
     "http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=1662&ver=2&st=1&stmp=1547629390761",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],

    ["zfcg_zhaobiao_shiji_gg",
     "http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=1665&ver=2&st=1&stmp=1547629395730",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],
    #
    ["zfcg_zhongbiao_shiji_gg",
     "http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=2014&ver=2&st=1&stmp=1547629484037",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],
    #
    ["zfcg_biangeng_shiji_gg",
     "http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=1663&ver=2&st=1&stmp=1547629438352",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],

    ["zfcg_gqita_he_yan_shiji_gg",
     "http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=2015&ver=2&st=1&stmp=1547629588834",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],

    ["zfcg_zhaobiao_danyilaiyuan_shiji_gg",
     "http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=2033&ver=2&st=1&stmp=1547629668070",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'zbfs': '单一来源'}), f2],

    ["zfcg_yucai_quxian_gg",
     "http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=1994&ver=2&stmp=1547629734075",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区级'}), f2],

    ["zfcg_zhaobiao_quxian_gg",
     "http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=1664&ver=2&stmp=1547629760509",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区级'}), f2],

    ["zfcg_zhongbiao_quxian_gg",
     "http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=2013&ver=2&stmp=1547629795283",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区级'}), f2],
    #
    ["zfcg_biangeng_quxian_gg",
     "http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=1666&ver=2&stmp=1547629779514",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区级'}), f2],

    ["zfcg_gqita_he_yan_quxian_gg",
     "http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=2016&ver=2&stmp=1547629811399",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区级'}), f2],

    ["zfcg_zhaobiao_danyilaiyuan_quxian_gg",
     "http://www.ccgp-tianjin.gov.cn/portal/topicView.do?method=view&view=Infor&id=2034&ver=2&stmp=1547629860833",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区级', 'zbfs': '单一来源'}), f2],
]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="天津市", **args)
    est_html(conp, f=f3, **args)


# 域名变更，页数太多，跑不完
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "tianjin"])
