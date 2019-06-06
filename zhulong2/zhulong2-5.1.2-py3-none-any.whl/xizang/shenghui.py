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

_name_ = "xizang_shenghui"


def f1(driver, num):
    locator = (By.XPATH, "//div[@id='news_div']/ul/li[1]/div/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//a[@class='currentY']")
        cnum = int(WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip())
    except:
        cnum = 1
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@id='news_div']/ul/li[1]/div/a").get_attribute('href').rsplit('/',
                                                                                                                maxsplit=1)[
            1]

        driver.execute_script('changePage({})'.format(num))

        locator = (By.XPATH, "//div[@id='news_div']/ul/li[1]/div/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    ul = soup.find("div", id='news_div').ul
    trs = ul.find_all("li")
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
            link = 'http://www.ccgp-xizang.gov.cn' + a['href'].strip()
        span = tr.find('span').text.strip()
        tmp = [title, span, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@id='news_div']/ul/li[1]/div/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        while True:
            val = driver.find_element_by_xpath("//div[@id='news_div']/ul/li[1]/div/a").get_attribute('href').rsplit('/',
                                                                                                                    maxsplit=1)[
                1]
            locator = (By.XPATH, "//a[@class='numberPages'][last()]")
            str_1 = int(WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip())
            driver.execute_script('changePage({})'.format(str_1))
            locator = (By.XPATH, "//div[@id='news_div']/ul/li[1]/div/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            locator = (By.XPATH, "//a[@class='numberPages'][last()]")
            str_2 = int(WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip())
            if str_1 > str_2:
                var = driver.find_element_by_xpath("//a[@class='prevYin']").text.strip()
                if var == '下一页':
                    num = str_1
                    break
    except:
        var_1 = driver.find_element_by_xpath("//a[@class='prevYin'][1]").text.strip()
        var_2 = driver.find_element_by_xpath("//a[@class='prevYin'][2]").text.strip()
        if (var_1 == '上一页') and (var_2 == '下一页'):
            num = 1
        else:
            raise TimeoutError
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='neirong'][string-length()>10]")
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
    div = soup.find('div', class_="neirong")
    return div


data = [
    ["zfcg_gqita_zhao_zhong_shengji_gg",
     "http://www.ccgp-xizang.gov.cn/shopHome/morePolicyNews.action?categoryId=124&areaParam=xizhang",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '省级'}), f2],
    # #
    ["zfcg_gqita_zhao_zhong_shixian_gg",
     "http://www.ccgp-xizang.gov.cn/shopHome/morePolicyNews.action?categoryId=125&areaParam=xizhang",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县'}), f2],
    # #
    ["zfcg_gqita_zhao_zhong_gg",
     "http://www.ccgp-xizang.gov.cn/shopHome/morePolicyNews.action?categoryId=124,125",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="西藏省省级", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "xizang"])
