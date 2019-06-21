import math
import time

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json

from zhulong4.util.etl import est_tbs, est_meta, est_html


_name_ = 'www_namkwong_com_mo'


def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="ajaxfy2"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('pageNum=(\d+)', url)[0]

    if num != int(cnum):
        val = driver.find_element_by_xpath('//ul[@class="ajaxfy2"]/li[1]/a').get_attribute('href')[-30:-5]
        url = re.sub('pageNum=(\d+)', 'pageNum=%s' % num, url)
        driver.get(url)
        locator = (By.XPATH, '//ul[@class="ajaxfy2"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', class_='ajaxfy2').find_all('li')
    for tr in div:
        href = tr.a['href']
        name = tr.a['title']
        ggstart_time = tr.span.get_text()
        if 'http' in href:
            href = href
        else:
            href = 'http://www.namkwong.com.mo' + href
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="ajaxfy2"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//span[@class="simple_pgTotalRecord"]').text
    total = math.ceil(int(total) / 15)
    total = int(total)
    driver.quit()

    return total



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="artcontent"]')
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    time.sleep(0.1)
    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 10: break

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_="artcontent")
    return div


data = [

    #包含招标,中标
    ["qy_gqita_zhao_zhong_gg", "http://www.namkwong.com.mo/col/col1817/index.html?uid=9503&pageNum=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="中国南光集团", **args)
    est_html(conp, f=f3, **args)


##lch
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch3", "www_namkwong_com_mo"])
