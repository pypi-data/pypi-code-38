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

_name_ = "xinjiang_hetian"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='news-list-l f_l']/ul[1]/li[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='pages mt50 tac']/strong")
        cnum = int(WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip())
    except:
        cnum = 1
    url = driver.current_url
    if num != int(cnum):
        val = \
        driver.find_element_by_xpath("//div[@class='news-list-l f_l']/ul[1]/li[1]//a").get_attribute('href').rsplit('/',
                                                                                                                    maxsplit=1)[
            1]
        if '&page' not in url:
            s = "&page=%d" % (num) if num > 1 else "&page=1"
            url += s
        elif num == 1:
            url = re.sub("page=[0-9]*", "page=1", url)
        else:
            s = "page=%d" % (num) if num > 1 else "page=1"
            url = re.sub("page=[0-9]*", s, url)
        driver.get(url)

        locator = (By.XPATH, "//div[@class='news-list-l f_l']/ul[1]/li[1]//a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    tbody = soup.find("div", class_='news-list-l f_l')
    uls = tbody.find_all("ul", class_='news-list-con')
    data = []
    for ul in uls:
        lis = ul.find_all('li')
        for li in lis:
            a = li.find("a")
            try:
                title = a['title'].strip()
            except:
                title = a.text.strip()
            href = a['href'].strip()
            if 'http' in href:
                link = href
            else:
                link = 'https://www.xjht.gov.cn' + a['href'].strip()
            span = li.find('span').text.strip()
            tmp = [title, span, link]
            data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='news-list-l f_l']/ul[1]/li[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='pages mt50 tac']/cite")
        str_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = re.findall(r'/(\d+)页', str_1)[0]
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='news-detail'][string-length()>10]")
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

    div = soup.find('div', class_="news-detail")
    return div


data = [
    ["zfcg_gqita_zhao_zhong_gg",
     "https://www.xjht.gov.cn/article/list.php?catid=20",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["zfcg_gqita_zhao_bian_gg",
     "https://www.xjht.gov.cn/article/list.php?catid=25",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhongbiao_gg",
     "https://www.xjht.gov.cn/article/list.php?catid=26",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="新疆省和田市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "hetian"])
