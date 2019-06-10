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

from zhulong2.util.etl import est_html, est_meta, add_info

_name_ = "ningxia_shenghui"


def f1(driver, num):
    locator = (By.XPATH, "//table[@class='newsTable listdt']/tbody/tr[1]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//p[@class='summary']")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(re.findall(r'第(\d+)页/', cnum)[0])
    except:
        cnum = 1
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@class='newsTable listdt']/tbody/tr[1]/td/a").get_attribute(
            'href').rsplit('/', maxsplit=1)[1]
        if '&page' not in url:
            s = "&page=%d" % (num - 1) if num > 1 else "&page=0"
            url += s
        elif num == 1:
            url = re.sub("page=[0-9]*", "page=0", url)
        else:
            s = "page=%d" % (num - 1) if num > 1 else "page=0"
            url = re.sub("page=[0-9]*", s, url)
        driver.get(url)

        locator = (By.XPATH, "//table[@class='newsTable listdt']/tbody/tr[1]/td/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    tbody = soup.find("table", class_='newsTable listdt').tbody
    trs = tbody.find_all("tr")
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
            link = 'http://www.ccgp-ningxia.gov.cn/public/NXGPPNEW/dynamic/' + a['href'].strip()
        span = tr.find('th', align="center").text.strip()
        tmp = [title, span, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//table[@class='newsTable listdt']/tbody/tr[1]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//p[@class='summary']")
        str_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = re.findall(r'/共(\d+)页', str_1)[0]
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='vT_z w100'][string-length()>10] | //div[@id='jjDiv'][string-length()>10]")
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
    div = soup.find('div', class_="vT_z w100")
    if div == None:
        div = soup.find('div', id='jjDiv')
    return div


data = [
    ["zfcg_zhaobiao_wsjj_shengji_gg",
     "http://www.ccgp-ningxia.gov.cn/public/NXGPPNEW/dynamic/contents/CGGG/JJGG/index.jsp?cid=328&sid=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '网上竞价', 'diqu': '区本级'}), f2],
    # #
    ["zfcg_zhaobiao_shengji_gg",
     "http://www.ccgp-ningxia.gov.cn/public/NXGPPNEW/dynamic/contents/CGGG/ZBGG/index.jsp?cid=316&sid=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区本级'}), f2],
    # #
    ["zfcg_zhongbiao_shengji_gg",
     "http://www.ccgp-ningxia.gov.cn/public/NXGPPNEW/dynamic/contents/CGGG/ZHBGG/index.jsp?cid=317&sid=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区本级'}), f2],
    # #
    ["zfcg_liubiao_shengji_gg",
     "http://www.ccgp-ningxia.gov.cn/public/NXGPPNEW/dynamic/contents/CGGG/GGGG/index.jsp?cid=318&sid=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区本级'}), f2],
    # #
    ["zfcg_biangeng_shengji_gg",
     "http://www.ccgp-ningxia.gov.cn/public/NXGPPNEW/dynamic/contents/CGGG/GZGG/index.jsp?cid=2004&sid=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区本级'}), f2],
    # #
    ["zfcg_zhaobiao_dyly_shengji_gg",
     "http://www.ccgp-ningxia.gov.cn/public/NXGPPNEW/dynamic/contents/CGGG/DYLYSHGS/index.jsp?cid=319&sid=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '单一来源', 'diqu': '区本级'}), f2],

    ["zfcg_zhaobiao_wsjj_shixian_gg",
     "http://www.ccgp-ningxia.gov.cn/public/NXGPPNEW/dynamic/contents/SXCGGG/JJGG/index.jsp?cid=2011&sid=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '网上竞价', 'diqu': '市县'}), f2],
    # #
    ["zfcg_zhaobiao_shixian_gg",
     "http://www.ccgp-ningxia.gov.cn/public/NXGPPNEW/dynamic/contents/SXCGGG/ZBGG/index.jsp?cid=2012&sid=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县'}), f2],
    # #
    ["zfcg_zhongbiao_shixian_gg",
     "http://www.ccgp-ningxia.gov.cn/public/NXGPPNEW/dynamic/contents/SXCGGG/ZHBGG/index.jsp?cid=2013&sid=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县'}), f2],
    # #
    ["zfcg_liubiao_shixian_gg",
     "http://www.ccgp-ningxia.gov.cn/public/NXGPPNEW/dynamic/contents/SXCGGG/GGGG/index.jsp?cid=2016&sid=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县'}), f2],
    # #
    ["zfcg_biangeng_shixian_gg",
     "http://www.ccgp-ningxia.gov.cn/public/NXGPPNEW/dynamic/contents/SXCGGG/GZGG/index.jsp?cid=2018&sid=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县'}), f2],
    # #
    ["zfcg_zhoabiao_dyly_shixian_gg",
     "http://www.ccgp-ningxia.gov.cn/public/NXGPPNEW/dynamic/contents/SXCGGG/DYLYSHGS/index.jsp?cid=2017&sid=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '单一来源', 'diqu': '市县'}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="宁夏省省级", **args)
    est_html(conp, f=f3, **args)


# 域名变更
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "ningxia"])
