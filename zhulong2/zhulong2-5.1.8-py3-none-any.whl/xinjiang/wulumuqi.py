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

_name_ = "xinjiang_wulumuqi"


def f1(driver, num):
    locator = (By.XPATH, "//table[@id='packTable']/tbody/tr[2]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//nobr[@id='packTableRowCount']")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(re.findall(r'(\d+)', cnum)[1])
        if cnum / 15 == int(cnum / 15):
            cnum = cnum / 15
        else:
            cnum = int(cnum / 15) + 1
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@id='packTable']/tbody/tr[2]/td/a").get_attribute('onclick')
        val = re.findall(r"\(this,'(.*)'\)", val)[0]
        driver.find_element_by_xpath("//input[@id='packTablePg']").clear()
        driver.find_element_by_xpath("//input[@id='packTablePg']").send_keys(num, Keys.ENTER)

        locator = (By.XPATH, "//table[@id='packTable']/tbody/tr[2]/td/a[not(contains(@onclick, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    tbody = soup.find("table", id='packTable').tbody
    trs = tbody.find_all("tr")
    data = []
    for tr in trs[1:]:
        a = tr.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        href = a['onclick'].strip()
        if 'http' in href:
            link = href
        else:
            infoid = re.findall(r"\(this,'(.*)'\)", href)[0]
            link = 'http://zfcg.wlmq.gov.cn/infopublish.do?method=infoPublishView&infoid=' + infoid
        span = tr.find('font', class_='tableListDate').text.strip()
        tmp = [title, span, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//table[@id='packTable']/tbody/tr[2]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//span[@id='packTablePageCount']")
        str_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = int(re.findall(r'(\d+)', str_1)[0])
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    if '404' in driver.title:
        return 404
    locator = (By.XPATH, "//div[@class='w_content_main'][string-length()>10]")
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

    div = soup.find('div', class_='w_content_main')
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "http://zfcg.wlmq.gov.cn/generalpage.do?method=showList&fileType=201704-002&faname=201704-001&num=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["zfcg_zhongbiao_gg",
     "http://zfcg.wlmq.gov.cn/generalpage.do?method=showList&fileType=201704-003&faname=201704-001&num=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_biangeng_gg",
     "http://zfcg.wlmq.gov.cn/generalpage.do?method=showList&fileType=201704-004&faname=201704-001&num=3",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_gqita_liu_zhongz_gg",
     "http://zfcg.wlmq.gov.cn/generalpage.do?method=showList&fileType=201704-005&faname=201704-001&num=4",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["zfcg_zhaobiao_dyly_gg",
     "http://zfcg.wlmq.gov.cn/generalpage.do?method=showList&fileType=201704-006&faname=201704-001&num=5",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '单一来源'}), f2],

    ["zfcg_gqita_zhao_liu_quxian_gg",
     "http://zfcg.wlmq.gov.cn/generalpage.do?method=showList&fileType=201705-002&faname=201705-001&num=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区县'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="新疆省乌鲁木齐市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "wulumuqi"])
