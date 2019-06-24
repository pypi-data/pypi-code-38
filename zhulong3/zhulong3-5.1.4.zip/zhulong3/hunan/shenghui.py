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

_name_ = 'hunan_shenghui'

def f1(driver, num):
    locator = (By.XPATH, '//tr[@class="trStyle"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//span[@id="ID_ucBiddingList_ucPager1_lbPage"]').text
    cnum = re.findall('(\d+)/', cnum)[0].strip()

    if cnum != str(num):
        val = driver.find_element_by_xpath('//tr[@class="trStyle"][1]//a').get_attribute('href')[-50:-30]

        select = Select(driver.find_element_by_xpath('//select[@class="dropdownlist"]'))
        select.select_by_value(str(num))
        driver.find_element_by_xpath('//input[@class="btn_blue"]').click()

        locator = (By.XPATH, '//tr[@class="trStyle"][1]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find_all('tr', class_='trStyle')
    for tr in trs:
        href = tr.a['href']
        name = tr.a['title'].strip()
        ggstart_time = tr.span.get_text().strip('(').strip(')')
        if 'http' in href:
            href = href
        else:
            href = 'http://www.hnztb.org' + href

        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//tr[@class="trStyle"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//span[@id="ID_ucBiddingList_ucPager1_lbPage"]').text
    total = re.findall(r'/(\d+)', total)[0].strip()
    total = int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//table[@id="Table3"][string-length()>20]')

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

    div = soup.find('table', id="Table3")

    return div


data = [

    ["gcjs_zhaobiao_gg", "http://www.hnztb.org/Index.aspx?action=ucBiddingList&modelCode=0003&ItemCode=000005001&name=%u5efa%u8bbe%u5de5%u7a0b%u62db%u6807%u4fe1%u606f",[ "name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://www.hnztb.org/Index.aspx?action=ucBiddingList&modelCode=0004&ItemCode=000009002&name=%u5efa%u7b51%u5de5%u7a0b%u4e2d%u6807%u516c%u793a",[ "name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_da_bian_gg", "http://www.hnztb.org/Index.aspx?action=ucBiddingList&modelCode=0006&ItemCode=000007001&name=%E6%8B%9B%E6%A0%87%E7%AD%94%E7%96%91",[ "name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg", "http://www.hnztb.org/Index.aspx?action=ucBiddingList&modelCode=0004&ItemCode=000009001&name=%u5efa%u7b51%u5de5%u7a0b%u4e2d%u6807%u7ed3%u679c",[ "name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖南省省会", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "hunan_shenghui"],headless=False,num=1)