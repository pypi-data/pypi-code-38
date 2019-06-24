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

_name_ = 'jiangsu_xuzhou'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='zw_contianer']")
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
    div = soup.find('div', class_='zw_contianer')
    return div


def f1(driver, num):
    locator = (By.XPATH, "//ul[@id='listIn_page']/li[1]/a")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//ul[@id='listIn_page']/li[1]/a").get_attribute("href")[-40:]

    cnum = driver.find_element_by_xpath("//font[2]").text
    # print('val', val, 'cnum', cnum)
    if int(cnum) != int(num):
        driver.execute_script("InitControl(%s)" % num)
        locator = (By.XPATH, '//ul[@id="listIn_page"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//ul[@id='listIn_page']/li")
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        ggstart_time = content.xpath('./em/text()')[0].strip()
        href = "http://www.ccgp-xuzhou.gov.cn/Home/" + content.xpath("./a/@href")[0].strip('.')
        temp = [name, ggstart_time, href]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//font")
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    total_page = driver.find_element_by_xpath("//font[1]").text

    # print('total_page', total_page)
    driver.quit()
    return int(total_page)


data = [
    #
    ["zfcg_yucai_shiji_gg", "http://www.ccgp-xuzhou.gov.cn/Home/HomeList?category_id=4",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'市级'}), f2],
    ["zfcg_zgys_shiji_gg", "http://www.ccgp-xuzhou.gov.cn/Home/HomeList?category_id=5",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'市级'}), f2],
    ["zfcg_zhaobiao_shiji_gg", "http://www.ccgp-xuzhou.gov.cn/Home/HomeList?category_id=331",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'市级'}), f2],
    ["zfcg_biangeng_shiji_gg", "http://www.ccgp-xuzhou.gov.cn/Home/HomeList?category_id=332",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'市级'}), f2],
    ["zfcg_zhongbiao_shiji_gg", "http://www.ccgp-xuzhou.gov.cn/Home/HomeList?category_id=333",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'市级'}), f2],
    ["zfcg_yanshou_shiji_gg", "http://www.ccgp-xuzhou.gov.cn/Home/HomeList?category_id=10",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'市级'}), f2],

    ["zfcg_yucai_xianji_gg", "http://www.ccgp-xuzhou.gov.cn/Home/HomeList?category_id=44",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'县级'}), f2],
    ["zfcg_zgys_xianji_gg", "http://www.ccgp-xuzhou.gov.cn/Home/HomeList?category_id=55",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'县级'}), f2],
    ["zfcg_zhaobiao_xianji_gg", "http://www.ccgp-xuzhou.gov.cn/Home/HomeList?category_id=334",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'县级'}), f2],
    ["zfcg_biangeng_xianji_gg", "http://www.ccgp-xuzhou.gov.cn/Home/HomeList?category_id=335",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'县级'}), f2],
    ["zfcg_zhongbiao_xianji_gg", "http://www.ccgp-xuzhou.gov.cn/Home/HomeList?category_id=336",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'县级'}), f2],
    ["zfcg_yanshou_xianji_gg", "http://www.ccgp-xuzhou.gov.cn/Home/HomeList?category_id=1010",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'县级'}), f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="江苏省徐州市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "jiangsu_xuzhou"])
