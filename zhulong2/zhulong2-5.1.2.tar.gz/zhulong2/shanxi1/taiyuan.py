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

_name_ = 'shanxi1_taiyuan'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="mainCont"]')
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
    div = soup.find('div', class_='mainCont')
    return div


def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='List_list']/li")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//ul[@class='List_list']/li/a").get_attribute("href")[-25:]

    cnum = int(driver.find_element_by_xpath("//span[@class='active']").text)
    # print('val', val, 'cnum', cnum)
    if int(cnum) != int(num):
        new_url = re.sub('index[_\d]*', 'index_' + str(num), driver.current_url)

        driver.get(new_url)
        locator = (By.XPATH, '//ul[@class="List_list"]/li/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@class="List_list"]/li')
    for content in content_list:
        name = content.xpath("./a/@title")[0].strip()
        # print(name)
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = "http://zfcg.taiyuan.gov.cn" + content.xpath("./a/@href")[0]
        temp = [name, ggstart_time, url]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    """山西太原政府采购只能查到20页数据。"""
    total_page = 20

    driver.quit()
    return int(total_page)


data = [
    #
    ["zfcg_zhaobiao_gg", "http://zfcg.taiyuan.gov.cn/zwxxgk/xxgg/cggg/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg", "http://zfcg.taiyuan.gov.cn/zwxxgk/xxgg/bcbggg/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg", "http://zfcg.taiyuan.gov.cn/zwxxgk/xxgg/zbgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="山西省太原市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "shanxi1_taiyuan"])
    # driver = webdriver.Chrome()
    # driver.get('http://zfcg.taiyuan.gov.cn/zwxxgk/xxgg/zbgg/index_2.shtml')
    # for i in range(1,10):
    #     f1(driver,i)
    # dr