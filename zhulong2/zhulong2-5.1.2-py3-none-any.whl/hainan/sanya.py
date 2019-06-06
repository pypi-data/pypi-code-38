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


_name_ = "hainan_sanya"


def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='line_li']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='pagination_index_num currentIndex']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(st)
    except:
        cnum = 1

    url = driver.current_url
    if num != cnum:
        val = driver.find_element_by_xpath("//ul[@class='line_li']/li[1]/a").get_attribute('href')[-15:]
        if 'list_' not in url:
            s = "list_%d" % (num) if num > 1 else "list"
            url = re.sub("list", s, url)
        elif num == 1:
            url = re.sub("list_[0-9]*", "list", url)
        else:
            s = "list_%d" % (num) if num > 1 else "list"
            url = re.sub("list_[0-9]*", s, url)
        driver.get(url)
        locator = (By.XPATH, "//ul[@class='line_li']/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("ul", class_='line_li')
    lis = div.find_all('li')
    data = []
    for tr in lis:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        td = tr.find('em').text.strip()
        if re.findall(r'\[(.*)\]', td):
            td = re.findall(r'\[(.*)\]', td)[0]
        link = a['href'].strip()
        if "http" in link:
            link = link
        else:
            link = 'http://www.sanya.gov.cn' + link
        tmp = [title, td, link]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//ul[@class='line_li']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//div[@class='pagination_index_last']")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = int(re.findall(r'(\d+)', st)[-1])
    driver.quit()
    return num



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@id='tblInfo'][string-length()>30] | //div[@class='nei03_02'][string-length()>30] | //div[@class='pages_content'][string-length()>30]")
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
    div = soup.find('table', id='tblInfo')
    if div == None:
        div = soup.find('div', class_='nei03_02')
        if div == None:
            div = soup.find('div', class_='pages_content')
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "http://www.sanya.gov.cn/sanyasite/cggg/simple_list.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://www.sanya.gov.cn/sanyasite/zbgg/simple_list.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="海南省三亚市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "sanya"])

