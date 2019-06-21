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
from zhulong3.util.etl import est_html, est_meta, add_info
import time

_name_ = 'anhui_huainan'


def f1(driver, num):
    driver.set_window_size(1366,768)
    locator = (By.XPATH, '//span[@class="current"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//div[@class="xxgk_nav_con"]/div[1]/ul/li/a').get_attribute("href")[-60:]
    cnum = driver.find_element_by_xpath('//span[@class="current"]').text
    locator = (By.XPATH, '//div[@class="xxgk_nav_con"]')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    if int(cnum) != int(num):
        driver.execute_script("window.scrollBy(0,document.body.scrollHeight)", "")
        driver.find_element_by_xpath('//div[@id="page_public_info"]/span/input').clear()
        driver.find_element_by_xpath('//div[@id="page_public_info"]/span/input').send_keys(num)
        driver.find_element_by_xpath('//div[@id="page_public_info"]/span/input').send_keys(Keys.ENTER)
        locator = (By.XPATH, '//div[@class="xxgk_nav_con"]/div[1]/ul/li/a[not(contains(@href,"%s"))]' % val)
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="xxgk_nav_con"]/div')
    for content in content_list:
        name = content.xpath("./ul/li/a/text()")[0].strip()
        url = content.xpath("./ul/li/a/@href")[0].strip()
        ggstart_time = content.xpath("./ul/li[last()]/text()")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print('temp', temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    driver.refresh()
    return df


def f2(driver):
    driver.set_window_size(1366,768)
    driver.execute_script("window.scrollBy(0,document.body.scrollHeight)", "")
    locator = (By.XPATH, '//span[@class="inputBar"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_page =re.findall(r"\/(\d+)页",driver.page_source)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@id="wenzhang"]')
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
    soup = BeautifulSoup(page, 'lxml')
    div = soup.find('div', id='wenzhang')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.huainan.gov.cn/public/column/4971417?type=4&catId=4977520&action=list",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_zhao_zhong_gc_gg",
     "http://www.huainan.gov.cn/public/column/4971417?type=4&catId=4977520&action=list",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'工程招投标'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="安徽省淮南市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "anhui_huainan"]
    work(conp)
    # chromeOption=webdriver.ChromeOptions()
    # chromeOption.add_argument('--headless')
    # chromeOption.add_argument('--no-sandbox')


    # driver = webdriver.Chrome(chrome_options=chromeOption)
    # driver.get("http://www.huainan.gov.cn/public/column/4971417?type=4&catId=4977520&action=list")
    # driver.maximize_window()
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 10)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://www.huainan.gov.cn/4971417/53806445.html'))
    # driver.close()
