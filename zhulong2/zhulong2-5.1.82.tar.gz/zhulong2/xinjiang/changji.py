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

_name_ = "xinjiang_changji"


def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='commonList_dot am-padding-sm']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//li[@class='am-active']")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        cnum = 1
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='commonList_dot am-padding-sm']/li[1]/a").get_attribute(
            'href').rsplit('/', maxsplit=1)[1]
        if '&cur_page' not in url:
            s = "&cur_page=%d" % (num) if num > 1 else "&cur_page=1"
            url += s
        elif num == 1:
            url = re.sub("cur_page=[0-9]*", "cur_page=1", url)
        else:
            s = "cur_page=%d" % (num) if num > 1 else "cur_page=1"
            url = re.sub("cur_page=[0-9]*", s, url)
        driver.get(url)

        locator = (By.XPATH, "//ul[@class='commonList_dot am-padding-sm']/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    tbody = soup.find("ul", class_='commonList_dot am-padding-sm')
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
            link = 'http://www.cjs.gov.cn' + a['href'].strip()
        span = tr.find('span', class_='a_date').text.strip()
        tmp = [title, span, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//ul[@class='commonList_dot am-padding-sm']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//ul[@class='am-pagination am-pagination-centered']/li[last()]/a")
        str_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')
        num = re.findall(r'page=(\d+)', str_1)[0]
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='am-u-sm-12'][string-length()>10]")
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

    div = soup.find('div', class_="article am-u-sm-12 am-u-md-11 am-u-lg-11 am-u-sm-centered am-link-muted")
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "http://www.cjs.gov.cn/info/iList.jsp?cat_id=28208",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["zfcg_gqita_zhong_liu_gg",
     "http://www.cjs.gov.cn/info/iList.jsp?cat_id=28209",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["zfcg_biangeng_gg",
     "http://www.cjs.gov.cn/info/iList.jsp?cat_id=28210",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="新疆省昌吉市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "changji"])
