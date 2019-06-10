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


_name_ = "hainan_haikou"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='list-c']/ul/li[1]/p[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='page']/font[@color='#FF0000']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(st)
    except:
        cnum = 1

    url = driver.current_url
    if num != cnum:
        val = driver.find_element_by_xpath("//div[@class='list-c']/ul/li[1]/p[1]/a").get_attribute('href')[-20:]
        if 'index' not in url:
            s = "index_%d.html" % (num-1) if num > 1 else "index.html"
            url += s
        elif num == 1:
            url = re.sub("index_[0-9]*", "index", url)
        else:
            s = "index_%d" % (num-1) if num > 1 else "index"
            url = re.sub("index_[0-9]*", s, url)
        driver.get(url)
        locator = (By.XPATH, "//div[@class='list-c']/ul/li[1]/p[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("div", class_='list-c')
    ul = div.find("ul")
    lis = ul.find_all('li')
    data = []
    for tr in lis:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        td = tr.find('span', class_="reltime").text.strip()
        if re.findall(r'(\d+-\d+-\d+)', td):
            td = re.findall(r'(\d+-\d+-\d+)', td)[0]
        else:td = None
        link = a['href'].strip()
        if "http" in link:
            href = link
        else:
            href = 'http://www.haikou.gov.cn/xxgk/szfbjxxgk/cztz/zfcg/cggg' + link.split('.', maxsplit=1)[1]
        tmp = [title, td, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='list-c']/ul/li[1]/p[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//div[@class='page']/a[last()]")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')
    num = int(re.findall(r'index_(\d+)', st)[0])+1
    driver.quit()
    return num



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='maincon'][string-length()>10]")
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
    div = soup.find('div', class_='maincon')
    return div


data = [
    ["zfcg_gqita_zhao_zhong_gg",
     "http://www.haikou.gov.cn/xxgk/szfbjxxgk/cztz/zfcg/cggg/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="海南省海口市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "haikou"],pageloadtimeout=60,pageLoadStrategy="none")
