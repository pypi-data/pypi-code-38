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

_name_ = "xinjiang_changji2"


def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='commonList_dot news_list']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//li[@class='active']")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='commonList_dot news_list']/li[1]/a").get_attribute('href')[-15:]
        if '&cur_page' not in url:
            s = "&cur_page=%d" % (num) if num > 1 else "&cur_page=1"
            url += s
        elif num == 1:
            url = re.sub("cur_page=[0-9]*", "cur_page=1", url)
        else:
            s = "cur_page=%d" % (num) if num > 1 else "cur_page=1"
            url = re.sub("cur_page=[0-9]*", s, url)
        driver.get(url)

        locator = (By.XPATH, "//ul[@class='commonList_dot news_list']/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    tbody = soup.find("ul", class_='commonList_dot news_list')
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
            link = 'http://www.cj.gov.cn' + a['href'].strip()
        span = tr.find('span', class_='newstime con_sm_hidden').text.strip()
        tmp = [title, span, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//ul[@class='commonList_dot news_list']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//ul[@class='pagination pagination']/li[last()]/a")
        str_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')
        num = re.findall(r'page=(\d+)', str_1)[0]
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='col-md-8'][string-length()>30]")
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

    div = soup.find('div', class_="col-md-8")
    return div


data = [
    ["zfcg_zhaobiao_lx1_gg",
     "http://www.cj.gov.cn/info/iList.jsp?cat_id=10484",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'采购信息'}), f2],

    ["zfcg_zhaobiao_gg",
     "http://www.cj.gov.cn/info/iList.jsp?cat_id=10485",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["zfcg_zhongbiao_gg",
     "http://www.cj.gov.cn/info/iList.jsp?cat_id=10486",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["zfcg_biangeng_gg",
     "http://www.cj.gov.cn/info/iList.jsp?cat_id=10487",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_zhao_zhong_gg",
     "http://www.cj.gov.cn/info/iList.jsp?cat_id=10488",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '分散采购'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="新疆省昌吉市", **args)
    est_html(conp, f=f3, **args)

# 网站新增：http://www.cj.gov.cn/index.htm
# 修改时间：2019/6/20
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "changji2"])

    # driver = webdriver.Chrome()
    # for d in data:
    #     driver.get(d[1])
    #     print(d[1])
    #     df = f2(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     df = f1(driver,3)
    #     print(df.values)
    #     for j in df[2].values:
    #         df = f3(driver, j)
    #         print(df)