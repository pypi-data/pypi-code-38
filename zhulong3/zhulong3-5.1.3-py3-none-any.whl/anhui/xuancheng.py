import math
import re

import requests
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong3.util.etl import est_html, est_meta
import time

_name_ = 'anhui_xuancheng'


def f1(driver, num):
    locator = (By.XPATH, '//*[@id="page_list"]/span[1]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//ul[@class="is-listnews"]/li[1]/a').get_attribute("href")[-60:]
    cnum_temp = driver.find_element_by_xpath('//*[@id="page_list"]/span[1]').text
    cnum = re.findall(r'(\d+) \/',cnum_temp)[0]
    locator = (By.XPATH, '//ul[@class="is-listnews"]/li')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    if int(cnum) != int(num):
        url = re.sub('page-\d+',"page-"+str(num),driver.current_url)
        driver.get(url)
        locator = (
        By.XPATH, '//ul[@class="is-listnews"]/li[1]/a[not(contains(@href,"%s"))]' % val)
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@class="is-listnews"]/li')
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        url = 'http://zjw.xuancheng.gov.cn'+content.xpath("./a/@href")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip().strip(']').strip('[')
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print('temp', temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//*[@id="page_list"]/span[1]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_temp = driver.find_element_by_xpath('//*[@id="page_list"]/span[1]').text
    total_page =re.findall("\/ (\d+)",total_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="is-contentbox"]')
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
    div = soup.find('div', class_='is-contentbox')
    return div


data = [
    ["gcjs_gqita_zhao_zhong_bu_gg",
     "http://zjw.xuancheng.gov.cn/content/channel/568dc13820f7fe83d49fb4e4/page-1/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="安徽省宣城市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "anhui_xuancheng"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://zjw.xuancheng.gov.cn/content/channel/568dc13820f7fe83d49fb4e4/page-6/")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 10)
    # print(f2(driver))
    #
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://zjw.xuancheng.gov.cn/content/detail/5ba3613020f7fe5112f6fef2.html'))
    # driver.close()