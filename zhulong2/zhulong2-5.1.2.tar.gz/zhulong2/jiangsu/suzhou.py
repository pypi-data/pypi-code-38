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

_name_ = 'jiangsu_suzhou'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='contain1' and @style='display: block;']")
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
    div = soup.find('div', attrs={'class': 'contain1', 'style': 'display: block;'})
    return div


def f1(driver, num):
    locator = (By.XPATH, "//ul[@id='searchid']/li[1]/span/a")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//ul[@id='searchid']/li[1]/span/a").get_attribute("href")[-40:]

    cnum = driver.find_element_by_xpath("//span[@id='pageIndex']").text
    if cnum == '':
        cnum = 1
    # print('val', val, 'cnum', cnum)
    if int(cnum) != int(num):
        driver.execute_script(
            "changePage($('#moreid').val(),$('#titles').val(),$('#choose').val(),$('#projectType').val(),$('#zbCode').val(),$('#appcode').val(),%s, page.rows)" % num)
        locator = (By.XPATH, '//ul[@id="searchid"]/li[1]/span/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//ul[@id='searchid']/li")
    for content in content_list:
        name = content.xpath("./span/a/text()")[0].strip()
        ggstart_time = content.xpath('./span[2]/text()')[0].strip().strip('[').strip(']')
        url = content.xpath("./span/a/@href")[0].split('/', maxsplit=1)[-1]
        href = "http://www.zfcg.suzhou.gov.cn/" + url
        temp = [name, ggstart_time, href]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//span[@id='totalPage']")
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    try:
        total_page = int(driver.find_element_by_xpath("//span[@id='totalPage']").text)
    except:
        total_page = 1
    driver.quit()
    return int(total_page)


data = [
    # #
    ["zfcg_zhaobiao_gg",
     "http://www.zfcg.suzhou.gov.cn/html/search.shtml?title=&choose=&projectType=0&zbCode=&appcode=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://www.zfcg.suzhou.gov.cn/html/search.shtml?title=&choose=&projectType=1&zbCode=&appcode=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://www.zfcg.suzhou.gov.cn/html/search.shtml?title=&choose=&projectType=2&zbCode=&appcode=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="江苏省苏州市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "jiangsu_suzhou"])
