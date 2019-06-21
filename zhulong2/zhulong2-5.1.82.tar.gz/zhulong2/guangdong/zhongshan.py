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

_name_ = "guangdong_zhongshan"



def f1(driver, num):
    url = driver.current_url
    locator = (By.XPATH, "//td[@class='cssArticleList']/ul/li[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//td[@class='cssCount']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = re.findall(r'第(\d+)页', st)[0]
    except:
        cnum = 1

    if num != int(cnum):
        val = driver.find_element_by_xpath("//td[@class='cssArticleList']/ul/li[last()]//a").get_attribute('href')[-30:]
        if "page=" not in url:
            s = "&page=%d" % (num) if num > 1 else "&page=1"
            url+=s
        elif num == 1:
            url = re.sub("page=[0-9]*", "page=1", url)
        else:
            s = "page=%d" % (num) if num > 1 else "page=1"
            url = re.sub("page=[0-9]*", s, url)
        driver.get(url)
        locator = (By.XPATH, "//td[@class='cssArticleList']/ul/li[last()]//a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("td", class_="cssArticleList").ul
    trs = div.find_all("li")
    data = []
    for tr in trs:
        a = tr.find('a')
        try:
            name = a['title'].strip()
        except:
            name = a.text.strip()
        ggstart_time = tr.find('span', class_='cssTime').text.strip()
        href = 'http://www.zhongshancz.gov.cn:8088/zfcg/' + a['href'].rsplit('../', maxsplit=1)[1]
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']= None
    return df


def f2(driver):
    locator = (By.XPATH, "//td[@class='cssArticleList']/ul/li[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//td[@class='cssCount']")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'共(\d+)页', st)[0]
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//td[@class='cssArticleContent'][string-length()>40]")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('td', class_='cssArticleContent')
    return div


data = [
    ["zfcg_zhaobiao_shizhi_gg", "http://www.zhongshancz.gov.cn:8088/zfcg/appFile/main/list.jsp?node=88",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu':'市直'}), f2],
    #
    ["zfcg_zhaobiao_zhenqu_gg", "http://www.zhongshancz.gov.cn:8088/zfcg/appFile/main/list.jsp?node=89",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '镇区'}), f2],

    ["zfcg_biangeng_gg", "http://www.zhongshancz.gov.cn:8088/zfcg/appFile/main/list.jsp?node=3",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg", "http://www.zhongshancz.gov.cn:8088/zfcg/appFile/main/list.jsp?node=4",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省中山市", **args)
    est_html(conp, f=f3, **args)


# 网站新增：http://www.zhongshancz.gov.cn:8088/zfcg/
# 修改时间：2019/6/20
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "zhongshan"])

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