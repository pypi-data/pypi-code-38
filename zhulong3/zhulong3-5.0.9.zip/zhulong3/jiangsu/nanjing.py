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

_name_ = 'jiangsu_nanjing'


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="fenye"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//div[@class="news_list_middle_right1"]/ul/li[1]/a').get_attribute("href")[-10:]
    cnum_temp = driver.find_element_by_xpath('//div[@class="fenye"]').text
    cnum = re.findall(r'(\d)+\/', cnum_temp)[0]
    locator = (By.XPATH, "//div[@class='news_list_middle_right1']/ul")
    # print(cnum, val)
    if int(cnum) != int(num):
        url = re.sub(r'page=\d+','page='+str(num),driver.current_url)
        # print(url)
        driver.get(url)
        locator = (By.XPATH, "//div[@class='news_list_middle_right1']/ul/li[1]/a[not(contains(@href,'%s'))]" % val)
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@class='news_list_middle_right1']/ul/li")
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        url = "http://njgcztbxh.com/" + content.xpath("./a/@href")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print('temp', temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="fenye"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_temp = driver.find_element_by_xpath('//div[@class="fenye"]').text
    total_page = re.findall(r'\/(\d+)', total_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="news_end_middle_right1"]')
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
    div = soup.find('div', class_='news_end_middle_right1')
    return div



data = [
    ["gcjs_zhaobiao_gg",
     "http://njgcztbxh.com/about.asp?pclassid=110&k=c&sclassid=111&key=&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://njgcztbxh.com/about.asp?pclassid=110&k=c&sclassid=112&key=&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_gg",
     "http://njgcztbxh.com/about.asp?pclassid=110&k=c&sclassid=113&key=&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="江苏省南京市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "jiangsu_nanjing"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://njgcztbxh.com/about.asp?pclassid=110&k=c&sclassid=111&key=&page=1")
    # f1(driver, 4)
    # f1(driver, 10)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://njgcztbxh.com/end.asp?id=2216'))
    # driver.close()
