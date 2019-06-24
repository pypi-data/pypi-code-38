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

_name_ = 'hunan_changsha1'

def f1(driver, num):
    locator = (By.XPATH, '//table[@id="SSSListModule1"]/tbody/tr[1]/td[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//table[@id="SSSListModule1"]/tfoot//td').text
    cnum = re.findall('第(\d+?)页', cnum)[0].strip()


    if cnum != str(num):
        val = driver.find_element_by_xpath('//table[@id="SSSListModule1"]/tbody/tr[1]/td[2]//a').get_attribute('href')[-30:-5]

        driver.execute_script('javascript:openPage(%s);' % (int(total_page) - num + 1))
        locator = (
        By.XPATH, '//table[@id="SSSListModule1"]/tbody/tr[1]/td[2]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find('table', id='SSSListModule1').find('tbody').find_all('tr')[:-1]
    for tr in trs:
        a_ = tr.find_all('a')
        href = a_[0]['href']
        name = a_[0].get_text()
        ggstart_time = a_[1].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.csjszbb.com' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)

    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    global total_page
    locator = (By.XPATH, '//table[@id="SSSListModule1"]/tbody/tr[1]/td[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath('//table[@id="SSSListModule1"]/tfoot//td').text

    total = re.findall(r'共(\d+?)页', total)[0].strip()
    total = int(total)
    total_page=total
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//div[@class="detail_c1"][string-length()>10]')

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

    div = soup.find('div', class_="detail_c1")

    return div


data = [

    ["gcjs_zhaobiao_gg", "http://www.csjszbb.com/zbbmh/bbxt/zbggfb/index.shtml",[ "name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_biangeng_gg", "http://www.csjszbb.com/zbbmh/zbbmh/zbwj/index.shtml",[ "name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_kongzhijia_gg", "http://www.csjszbb.com/zbbmh/zbbmh/zgtbxjgs/index.shtml",[ "name", "ggstart_time", "href", "info"], f1, f2],
    #包含结果,中标hx
    ["gcjs_zhongbiaohx_gg", "http://www.csjszbb.com/zbbmh/zbbmh/zbxx/index.shtml",[ "name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zgys_gg", "http://www.csjszbb.com/zbbmh/zbbmh/zbxx/zgsctz/index.shtml",[ "name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_da_bian_gg", "http://www.csjszbb.com/zbbmh/zbbmh/zbdywj/index.shtml",[ "name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖南省长沙市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "hunan_changsha1"])