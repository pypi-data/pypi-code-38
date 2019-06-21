import math
import re

import requests
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong4.util.etl import est_html, est_meta
import time

_name_ = 'bidding_ceiec_com_cn'


def f1(driver, num):
    driver.set_window_size(1366,768)
    locator = (By.XPATH, '//div[@class="infolist-main bidlist"]/ul/li')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//div[@class="infolist-main bidlist"]/ul/li[1]/a').get_attribute("href")[-15:]
    cnum = driver.find_element_by_xpath('//div[@class="pag-txt"]/em[1]').text
    locator = (By.XPATH, '//div[@class="infolist-main bidlist"]/ul/li')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    if int(cnum) != int(num):
        url = re.sub('index[_\d]{0,5}\.jhtml','index.jhtml' if num == 1 else 'index_'+str(num)+'.jhtml',driver.current_url)
        # print(url)
        driver.get(url)
        locator = (By.XPATH, '//div[@class="infolist-main bidlist"]/ul/li[1]/a[not(contains(@href,"%s"))]' % val)
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="infolist-main bidlist"]/ul/li')
    for content in content_list:
        name = content.xpath("./a/span/text()")[0].strip()
        url = content.xpath("./a/@href")[0].strip()
        ggstart_time = 'None'
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print('temp', temp)
    df = pd.DataFrame(data=data)
    df["info"] = None

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="pag-txt"]/em[2]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_page = driver.find_element_by_xpath('//div[@class="pag-txt"]/em[2]').text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="article-content"]')
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
    div = soup.find('div', class_='article-content')
    return div


data = [
    ["qy_zhaobiao_gg",
     "http://bidding.ceiec.com.cn/zbgg/index.jhtml",
     ["name", "ggstart_time", "href",  "info"], f1, f2],
    ["qy_biangeng_gg",
     "http://bidding.ceiec.com.cn/bggg/index.jhtml",
     ["name", "ggstart_time", "href",  "info"], f1, f2],
    ["qy_zhongbiao_gg",
     "http://bidding.ceiec.com.cn/zbgs/index.jhtml",
     ["name", "ggstart_time", "href",  "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="中国电子进出口总公司", **args)
    est_html(conp, f=f3, **args)

if __name__ == "__main__":

    conp = ["postgres", "since2015", "192.168.3.171", "anbang_qiye", "bidding_ceiec_com_cn"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://bidding.ceiec.com.cn/zbgg/index.jhtml")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 10)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://bidding.ceiec.com.cn/bggg/5235.jhtml'))
    # driver.close()
