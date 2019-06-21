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

from zhulong3.util.etl import est_tbs, est_meta, est_html, est_meta_large

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url = "http://www.fzztb.com/CmsPortalWeb/main/project.xhtml"
# driver = webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_ = 'jiangxi_jiujiang'


def f1(driver, num):
    locator = (By.XPATH, '//li[@class="wb-data-list"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = int(driver.find_element_by_xpath('//div[@class="ewb-page"]//li[contains(@class,"current")]/a').text)
    if cnum == 1:
        cnum=0

    if cnum != num:
        val = driver.find_element_by_xpath('//li[@class="wb-data-list"][1]//a').get_attribute('href')[-30:-5]

        driver.execute_script("ShowAjaxNewPage(window.location.pathname,'categorypagingcontent',%s)"%num)
        locator = (By.XPATH, '//li[@class="wb-data-list"][1]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find_all('li', class_="wb-data-list")

    for tr in trs:
        href = tr.find('a')['href']
        name = tr.find('a').get_text()
        ggstart_time = tr.find('span').get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.jjjsgczbtb.com' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)

    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//li[@class="wb-data-list"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    val = driver.find_element_by_xpath('//li[@class="wb-data-list"][1]//a').get_attribute('href')[-30:-5]

    driver.execute_script("ShowAjaxNewPage(window.location.pathname,'categorypagingcontent',2)")
    locator = (By.XPATH, '//li[@class="wb-data-list"][1]//a[not(contains(@href,"{}"))]'.format(val))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//div[@class="ewb-page"]//li[last()-3]/a').text

    total = re.findall('/(\d+)$', total)[0].strip()
    total = int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//div[@id="mainContent"][string-length()>10]')

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

    div = soup.find('div', id="mainContent")

    return div


data = [

    ["gcjs_zhaobiao_gg", "http://www.jjjsgczbtb.com/jsgczbw/zbgg/",[ "name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://www.jjjsgczbtb.com/jsgczbw/zbgs/",[ "name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):

    est_meta(conp, data=data,diqu="江西省九江市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "jiangxi_jiujiang"],headless=False,num=1,pageLoadStrategy='none')