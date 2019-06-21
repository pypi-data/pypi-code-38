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

_name_ = "guangxi_wuzhou"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='md']/div/ul/li[1]/span/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//li[@class='current']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(str)
    except:
        cnum = 1

    url = driver.current_url
    if num != cnum:
        val = driver.find_element_by_xpath("//div[@class='md']/div/ul/li[1]/span/a").get_attribute('href')[-6:]
        if '?pageNo' not in url:
            s = "?pageNo=%d" % (num) if num > 1 else "?pageNo=1"
            url += s
        elif num == 1:
            url = re.sub("pageNo=[0-9]*", "pageNo=1", url)
        else:
            s = "pageNo=%d" % (num) if num > 1 else "pageNo=1"
            url = re.sub("pageNo=[0-9]*", s, url)
        driver.get(url)
        locator = (By.XPATH, "//div[@class='md']/div/ul/li[1]/span/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("div", class_='md')
    ul = div.find('ul')
    lis = ul.find_all('li')
    data = []
    for tr in lis:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        td = tr.find('span', style="width: 110px;float: right;").text.strip()
        link = 'http://www.wuzhou.gov.cn:8090' + a['href'].strip()
        try:
            span = tr.find('span', style="width: 90px;float: left;").text.strip()
            info = {'diqu': '{}'.format(span)}
            info = json.dumps(info, ensure_ascii=False)
        except:
            info = None
        tmp = [title, td, link, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='md']/div/ul/li[1]/span/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//p[@class='tz']/span[2]")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = int(str)
    except:
        num = 1
    driver.quit()
    return num


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='contain'][string-length()>10] | //div[@class='Section1'][string-length()>10]")
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
    div = soup.find('div', class_='contain')
    if div == None:
        div = soup.find('body')
    return div


data = [
    ["zfcg_zhaobiao_shiji_gg",
     "http://www.wuzhou.gov.cn:8090/web/cgw/cggglist_s.ptl",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # # #
    ["zfcg_zhongbiao_shiji_gg",
     "http://www.wuzhou.gov.cn:8090/web/cgw/zbhcbgglist_s.ptl",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_biangeng_shiji_gg",
     "http://www.wuzhou.gov.cn:8090/web/cgw/bcgzgglist_s.ptl",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # # #
    ["zfcg_gqita_zbwj_shiji_gg",
     "http://www.wuzhou.gov.cn:8090/web/cgw/zbwjygs_s.ptl",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '市级招标文件预公示'}), f2],
    ###
    ["zfcg_zhaobiao_xianqu_gg",
     "http://www.wuzhou.gov.cn:8090/web/cgw/cggglist.ptl",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # # #
    ["zfcg_zhongbiao_xianqu_gg",
     "http://www.wuzhou.gov.cn:8090/web/cgw/zbhcbgglist.ptl",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_biangeng_xianqu_gg",
     "http://www.wuzhou.gov.cn:8090/web/cgw/bcgzgglist.ptl",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # # #
    ["zfcg_gqita_zbwj_xianqu_gg",
     "http://www.wuzhou.gov.cn:8090/web/cgw/zbwjygs.ptl",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '县区招标文件预公示'}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广西省梧州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "wuzhou"])
