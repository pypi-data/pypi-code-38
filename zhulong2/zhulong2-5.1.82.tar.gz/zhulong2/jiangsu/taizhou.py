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

_name_ = 'jiangsu_taizhou'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//td[@height='124']")
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
    div = soup.find('td', height='124')
    return div


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="default_pgContainer"]//tr/td/a')
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//div[@class="default_pgContainer"]//tr[1]/td/a').get_attribute("href")[-30:]

    cnum = driver.find_element_by_xpath("//input[@class='default_pgCurrentPage']").get_attribute('value')
    # print('val', val, 'cnum', cnum)
    if int(cnum) != int(num):
        url = driver.current_url
        url = re.sub(r'pageNum=\d+', 'pageNum=' + str(num), url)
        driver.get(url)
        locator = (By.XPATH, '//div[@class="default_pgContainer"]//tr[1]/td/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="default_pgContainer"]//tr')
    for content in content_list:
        name = content.xpath("./td/a/text()")[0].strip()
        ggstart_time = content.xpath('./td[3]/text()')[0].strip()
        href = "http://tzzfcg.taizhou.gov.cn" + content.xpath("./td/a/@href")[0].strip()
        temp = [name, ggstart_time, href]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//span[@class='default_pgTotalPage']")
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    total_page = driver.find_element_by_xpath("//span[@class='default_pgTotalPage']").text

    # print('total_page', total_page)
    driver.quit()
    return int(total_page)


data = [
    #
    ["zfcg_yucai_gg", "http://tzzfcg.taizhou.gov.cn/col/col39324/index.html?uid=84961&pageNum=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_gg", "http://tzzfcg.taizhou.gov.cn/col/col50754/index.html?uid=83711&pageNum=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_danyilaiyuan_gg", "http://tzzfcg.taizhou.gov.cn/col/col43226/index.html?uid=64332&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'单一来源'}), f2],
    ["zfcg_biangeng_gg", "http://tzzfcg.taizhou.gov.cn/col/col39326/index.html?uid=84961&pageNum=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://tzzfcg.taizhou.gov.cn/col/col50755/index.html?uid=83711&pageNum=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_gg", "http://tzzfcg.taizhou.gov.cn/col/col43576/index.html?uid=84961&pageNum=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="江苏省泰州市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "jiangsu_taizhou"])
