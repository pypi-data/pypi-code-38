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

_name_ = "guangxi_baise"


def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='label_ul_b new_li6']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@id='page']/span")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(st)
    except:
        cnum = 1

    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='label_ul_b new_li6']/li[1]/a").get_attribute('href')[-20:]
        if 'html' not in url:
            s = "-%d.html" % (num) if num > 1 else "-1.html"
            url = re.sub("\.shtml", s, url)
        elif num == 1:
            url = re.sub("-[0-9]*\.html", "-1.html", url)
        else:
            s = "-%d.html" % (num) if num > 1 else "-1.html"
            url = re.sub("-[0-9]*\.html", s, url)
            # print(cnum)
        driver.get(url)
        locator = (By.XPATH, "//ul[@class='label_ul_b new_li6']/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    ul = soup.find("ul", class_='label_ul_b new_li6')
    lis = ul.find_all('li', class_=None)
    data = []
    for tr in lis:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        td = tr.find('span', class_="label_datatime").text.strip()
        td = re.findall(r'\[(.*)\]', td)[0]
        href = a['href'].strip()
        if 'http' in href:
            link = href
        else:
            link = 'http://czj.baise.gov.cn/' + href
        tmp = [title, td, link]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//ul[@class='label_ul_b new_li6']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@id='page']/a[last()-1]")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = int(st)
    except:
        num = 1
    driver.quit()
    return num


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='rightbox'][string-length()>10]")
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
    div = soup.find('div', id='rightbox')
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "http://czj.baise.gov.cn/list-55-1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhongbiao_gg",
     "http://czj.baise.gov.cn/list-54-1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["zfcg_biangeng_gg",
     "http://czj.baise.gov.cn/list-53-1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["zfcg_gqita_gg",
     "http://czj.baise.gov.cn/list-52-1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


# 网址变更,需要删除gg,重跑
def work(conp, **args):
    est_meta(conp, data=data, diqu="广西省百色市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "baise"])
