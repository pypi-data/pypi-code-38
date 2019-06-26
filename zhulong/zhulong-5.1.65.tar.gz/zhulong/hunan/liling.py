import pandas as pd
import re

from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write, db_command, db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html,add_info

_name_ = "liling"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='list_info']/div/ul/li")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = int(re.findall("(\d+)/", driver.find_element_by_xpath("//div[@class='page']/ul").text)[0])
    val = driver.find_element_by_xpath("//div[@class='list_info']/div/ul/li/div/a").get_attribute("href")[-25:]
    if cnum != num:
        if "index" in url:
            url = re.sub("([0-9]{1,})\.", str(num) + ".", url)
        else:
            url = url+"index_"+str(num)+".html"
        driver.get(url)
        locator = (By.XPATH, "//div[@class='list_info']/div/ul/li/div/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    body = etree.HTML(page)
    data = []
    content_list = body.xpath("//div[@class='list_info']/div/ul/li")

    for content in content_list:
        name = content.xpath("./div/a/text()")[0].strip()
        ggstart_time = content.xpath("./div[2]/text()")[0].strip()
        url = content.xpath("./div/a/@href")[0].strip()
        tmp = [name, ggstart_time, url]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None

    return df


def f2(driver):
    locator = (By.CLASS_NAME, "page")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    val = driver.find_element_by_xpath("//div[@class='page']/ul").text
    total = int(re.findall("/(\d+)", val)[0])
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.ID, "article_content")

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
    div = soup.find('div', id='article_content')
    return div


data = [
    ["gcjs_zhaobiao_gg", "http://llztb.org.cn/gcjs/1/",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg","http://llztb.org.cn/gcjs/2/",["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://llztb.org.cn/zfcg/1/",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiaohx_gg", "http://llztb.org.cn/zfcg/2/",["name", "ggstart_time", "href", "info"], f1, f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖南省醴陵市", **args)
    est_html(conp, f=f3, **args)
"""
网址无法访问。
时间2019年5月27日16:25:43
"""

if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "hunan", "liling"],num=1)

