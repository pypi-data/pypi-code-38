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
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json

from zhulong3.util.etl import est_tbs, est_meta, est_html

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url = "http://www.fzztb.com/CmsPortalWeb/main/project.xhtml"
# driver = webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_ = 'hunan_shaoyang'

def f1(driver, num):
    locator = (By.XPATH, '//div[@class="list005 h500"]//li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall(r'_(\d+?).html$', url)[0]

    if cnum != str(num):
        val = driver.find_element_by_xpath('//div[@class="list005 h500"]//li[1]/a').get_attribute('href')[-15:-5]

        url = url.rsplit('_', maxsplit=1)[0] + '_%s.html' % num

        driver.get(url)

        locator = (By.XPATH, '//div[@class="list005 h500"]//li[1]/a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find('div', class_='list005 h500').find_all('li')
    for tr in trs:
        href = tr.a['href']
        name = tr.a['title']
        name = re.findall('标题：(.+)发表时间', name)[0].strip()
        ggstart_time = tr.span.get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://zj.shaoyang.gov.cn/' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="list005 h500"]//li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath('//div[@class="pager"]/a[last()]').get_attribute('href')
    try:
        total = re.findall(r'_(\d+?).html', total)[0].strip()
        total = int(total)
    except:
        total=1
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//td[@class="c_content_overflow"][string-length()>10]')

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
        if i > 5: break

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    div = soup.find('td', class_="c_content_overflow")

    return div


data = [

    ["gcjs_zhaobiao_gg", "http://zj.shaoyang.gov.cn/Node-5017_1.html",[ "name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_da_bian_gg", "http://zj.shaoyang.gov.cn/Node-5020_1.html",[ "name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://zj.shaoyang.gov.cn/Node-5022_1.html",[ "name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg", "http://zj.shaoyang.gov.cn/Node-8557_1.html",[ "name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖南省邵阳市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "hunan_shaoyang"])