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

_name_ = 'heilongjiang_qqhaer'


def f1(driver, num):
    locator = (By.XPATH, '//li[@class="ewb-page-li ewb-pagelink-border current"]')
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        cnum = driver.find_element_by_xpath('//li[@class="ewb-page-li ewb-pagelink-border current"]').text
    except:
        cnum = 1

    val = driver.find_element_by_xpath('//ul[@class="wb-data-item"]/li/div/a').get_attribute("href")[-30:]
    locator = (By.XPATH, '//ul[@class="wb-data-item"]/li')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    # print(cnum,val)
    if int(cnum) != int(num):
        url = re.sub(r"\/[about\d]+.html", '/%s.html' % (num if str(num) != '1' else 'about'), driver.current_url)
        # print(url)
        driver.get(url)
        locator = (By.XPATH, '//ul[@class="wb-data-item"]/li/div/a[not(contains(text(),"%s"))]' % val)
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@class="wb-data-item"]/li')
    for content in content_list:
        name = content.xpath("./div/a/text()")[0].strip()
        url = "http://221.209.61.7" + content.xpath("./div/a/@href")[0].strip()
        try:
            ggstart_time = content.xpath("./span/text()")[0].strip()
        except:ggstart_time = ''
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print('temp', temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//span[@id="index"]')
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        total_temp = driver.find_element_by_xpath('//span[@id="index"]').text
        total_page = re.findall(r'\/(\d+)', total_temp)[0]
    except:
        total_page = 1
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="ewb-art"]')
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
    div = soup.find('div', class_='ewb-art')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://221.209.61.7/jyxx/003001/003001001/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_biangeng_gg",
     "http://221.209.61.7/jyxx/003001/003001002/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://221.209.61.7/jyxx/003001/003001003/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://221.209.61.7/jyxx/003001/003001004/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="黑龙江省齐齐哈尔市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "heilongjiang_qqhaer"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://221.209.61.7/jyxx/003001/003001001/about.html")
    # f1(driver, 4)
    # f1(driver, 10)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://221.209.61.7/jyxx/003001/003001001/20190306/e3eb8b56-3845-4ba2-974d-871a0e41e191.html'))
    # driver.close()
