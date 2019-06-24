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

_name_ = "guangxi_fangchenggang"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='news_list']/ul/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//span[@class='current']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(st)
    except:
        cnum = 1

    url = driver.current_url
    if num != cnum:
        val = driver.find_element_by_xpath("//div[@class='news_list']/ul/li[1]/a").get_attribute('href')[-12:]
        if num == 1:
            url = re.sub("/[0-9]*\.aspx", "/1.aspx", url)
        else:
            s = "/%d.aspx" % (num) if num > 1 else "/1.aspx"
            url = re.sub("/[0-9]*\.aspx", s, url)
            # print(cnum)
        driver.get(url)
        locator = (By.XPATH, "//div[@class='news_list']/ul/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("div", class_='news_list')
    ul = div.find('ul')
    lis = ul.find_all('li')
    data = []
    for tr in lis:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        td = tr.find('span', style="color:#ccc; float:right;").text.strip()
        td = re.findall(r'\[(.*)\]', td)[0]
        link = 'http://www.fcgszfcg.gov.cn' + a['href'].strip()
        try:
            span = tr.find('span', style="color:#FF6300;").text.strip()
            info = {'zbfs': '{}'.format(span)}
            info = json.dumps(info, ensure_ascii=False)
        except:
            info = None
        tmp = [title, td, link, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='news_list']/ul/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='flickr']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = int(re.findall(r'(\d+)', st)[-1])
    except:
        num = 1
    driver.quit()
    return num


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='wrap'][string-length()>10]")
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
    div = soup.find('div', class_='wrap')
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "http://www.fcgszfcg.gov.cn/cpurchase/5/1.aspx",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhongbiao_gg",
     "http://www.fcgszfcg.gov.cn/cpurchase/7/1.aspx",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_biangeng_gg",
     "http://www.fcgszfcg.gov.cn/cpurchase/6/1.aspx",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_gqita_zbwj_gg",
     "http://www.fcgszfcg.gov.cn/cpurchase/32/1.aspx",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '采购预公示'}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广西省防城港市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "fangchenggang"])
