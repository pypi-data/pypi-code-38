import random

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

_name_ = 'neimenggu_eerduosi'


def f3(driver, url):
    driver.get(url)
    time.sleep(random.randint(2, 5))
    locator = (By.XPATH, '//table[@align="center" and @width="95%"]')
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
    div = soup.find('table', width='95%')
    time.sleep(random.randint(5, 10))
    return div


def f1(driver, num):
    time.sleep(random.randint(15,20))
    locator = (By.XPATH, '//td[@valign="top" and @width="747"]//tbody//table[@width="93%"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//td[@valign="top" and @width="747"]//tbody//table[@width="93%"][1]//a').get_attribute("href")[-30:]
    cnum = int(driver.find_element_by_xpath('//span[@class="pagesize"]//span[@style="color:#FF0000;"]').text)

    if int(cnum) != int(num):
        url = driver.current_url
        url = url.rsplit('/', maxsplit=1)[0] + '/index_' + str(num) + '.html'
        driver.get(url)
        locator = (By.XPATH, '//td[@valign="top" and @width="747"]//tbody//table[@width="93%%"][1]//a[not(contains(@href,"%s"))]' % val)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    url_part = driver.current_url.split('/')[3]

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//td[@valign="top" and @width="747"]//tbody//table[@width="93%"]')
    for content in content_list:
        name = content.xpath(".//a/text()")[0].strip()
        ggstart_time = content.xpath(".//td[contains(string(),'-')]/text()")[0].strip('[').strip(']')
        url = "http://zfcg.ordos.gov.cn/"+url_part+ content.xpath(".//a/@href")[0].strip('.')
        temp = [name, ggstart_time, url]

        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    time.sleep(random.randint(2,10))
    locator = (By.XPATH, '//span[@class="pagesize"]')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    page = driver.find_element_by_xpath('//span[@class="pagesize"]').text
    total_page = re.findall('共(\d+)页',page)[0]
    driver.quit()
    return int(total_page)



data = [
    ["zfcg_zhaobiao_gg", "http://zfcg.ordos.gov.cn/zfcggg/", ["name", "ggstart_time", "href", "info"],f1, f2],

    # ["zfcg_zhongbiao_gg", "http://zfcg.ordos.gov.cn/zbgg1/", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_qiqu_gg", "http://zfcg.ordos.gov.cn/qqzfcggg/", ["name", "ggstart_time", "href", "info"], f1, f2],

    # ["zfcg_zhongbiao_qiqu_gg", "http://zfcg.ordos.gov.cn/qqzbgg/", ["name", "ggstart_time", "href", "info"], f1, f2],
    # 找不到

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="内蒙古鄂尔多斯市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "neimenggu_eerduosi"])
