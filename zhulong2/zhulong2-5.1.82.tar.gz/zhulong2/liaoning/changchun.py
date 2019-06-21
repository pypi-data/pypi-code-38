import math

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

from zhulong2.util.etl import est_meta, est_html, add_info

_name_ = 'liaoning_changchun'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="details"]')
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
    div = soup.find('div', class_='details')
    return div


def f1(driver, num):
    locator = (By.XPATH, '//table[@id="row"]/tbody/tr[1]/td/a')
    val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute("href")[-50:]

    locator = (By.XPATH, '//span[@class="pagelinks"]/font/strong')
    cnum = int(WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text)

    # print('val', val, 'cnum', cnum,'num',num)
    if int(cnum) != int(num):
        new_url = re.sub('p=\d+', 'p=' + str(num), driver.current_url)
        driver.get(new_url)
        locator = (By.XPATH, '//table[@id="row"]/tbody/tr[1]/td/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@id="row"]/tbody/tr')
    for content in content_list:
        name = content.xpath("./td[@class='tit']/a/text()")[0].strip()
        ggstart_time = content.xpath("./td[@class='time']/text()")[0].strip()
        url = "http://www.cczfcg.gov.cn" + content.xpath("./td/a/@href")[0]
        temp = [name, ggstart_time, url]

        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//span[@class='pagebanner']")
    txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text
    total_temp = int(re.findall('(\d+)', txt)[0])
    total_page = math.ceil(total_temp / 20)
    driver.quit()
    return int(total_page)


data = [

    ["zfcg_zhaobiao_sj_gg",
     "http://www.cczfcg.gov.cn/article/bid_list.action?__fp=xTwapxltBMnpSsXN23uINw%3D%3D&field=1&title=&d-16544-p=1&getList=&getList=%E6%90%9C%E7%B4%A2&_sourcePage=2BVgADW7Hx6FNrAm9GCx-F0umL1uqkNLHg3gos_i5uo%3D&type=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '市级'}), f2],
    ["zfcg_zhaobiao_qx_gg",
     "http://www.cczfcg.gov.cn/article/bid_list.action?field=2&d-16544-p=1&getList=&type=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '区县'}), f2],
    ["zfcg_zhaobiao_wf_gg",
     "http://www.cczfcg.gov.cn/article/news_list.action?d-16544-p=1&getList=&type=13",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '外阜'}), f2],

    ["zfcg_zhongbiao_sj_gg",
     "http://www.cczfcg.gov.cn/article/bid_list.action?field=1&d-16544-p=1&getList=&type=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '市级'}), f2],
    ["zfcg_zhongbiao_qx_gg",
     "http://www.cczfcg.gov.cn/article/bid_list.action?field=2&d-16544-p=1&getList=&type=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '区县'}), f2],
    ["zfcg_zhongbiao_wf_gg",
     "http://www.cczfcg.gov.cn/article/news_list.action?d-16544-p=1&getList=&type=14",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '外阜'}), f2],



]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="辽宁省长春市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "liaoning_changchun"], pageloadtimeout=60, pageloadstrategy='none',num=1)
    # driver= webdriver.Chrome()
    # driver.get('http://www.cczfcg.gov.cn/article/bid_list.action?__fp=xTwapxltBMnpSsXN23uINw%3D%3D&field=1&title=&d-16544-p=1&getList=&getList=%E6%90%9C%E7%B4%A2&_sourcePage=2BVgADW7Hx6FNrAm9GCx-F0umL1uqkNLHg3gos_i5uo%3D&type=1')
    # print(f2(driver))
    # f1(driver,2)
    # print(f3(driver, 'http://www.cczfcg.gov.cn/article/ShowInviteBid.action?showInvite=&project_id=1E109F87A4136398CFCE1D9F7F889276BCE02CD2C8276DF574E33519E0A34D1A'))
