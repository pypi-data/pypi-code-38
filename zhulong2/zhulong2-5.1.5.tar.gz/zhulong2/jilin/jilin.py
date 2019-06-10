import json

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

from zhulong2.util.etl import est_meta, est_html

_name_ = 'jilin_jilin'


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="listpage_content"]')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
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
    div = soup.find('div', class_='listpage_content')

    return div


def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="listpage_right_ul"]/li/a')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//ul[@class="listpage_right_ul"]/li[1]/a').get_attribute("href")[-30:]
    cnum =  driver.find_element_by_xpath('//a[@style="color:red"]/span').text
    url = driver.current_url

    # print('val', val, 'cnum', cnum,'num',num)
    if int(cnum) != int(num):
        url = re.sub(r"index[^\.]{0,}\.", 'index_'+str(num)+'.', url)
        # print(url)
        driver.get(url)
        locator = (By.XPATH, '//ul[@class="listpage_right_ul"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    url_pre = url.rsplit('/',maxsplit=1)[0]
    content_list = body.xpath('//ul[@class="listpage_right_ul"]/li')
    for content in content_list:
        name = content.xpath("./a/div[1]/text()")[0].strip()
        ggstart_time = content.xpath("./a/div[2]/text()")[0].strip().strip('[').strip(']')
        href = url_pre + content.xpath("./a/@href")[0].strip('.')
        temp = [name, ggstart_time, href]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//*[@id="fenye"]/a[last()]')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    total_page = re.findall('index_(\d+)', driver.find_element_by_xpath('//*[@id="fenye"]/a[last()]').get_attribute('href'))[0]
    driver.quit()
    return int(total_page)+1


data = [

    ["zfcg_zhongbiao_gg","http://www.jlcity.gov.cn/zw/zfcg/zbgg/index.html",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_gg","http://www.jlcity.gov.cn/zw/zfcg/cgxx/index.html",["name", "ggstart_time", "href", "info"], f1, f2],

    # 验收公示，需求公示，都无法访问
]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="吉林省吉林市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "jilin_jilin"], pageloadtimeout=60,
         pageloadstrategy='none')
