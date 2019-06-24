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

from zhulong3.util.etl import est_tbs, est_meta, est_html

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url = "http://www.fzztb.com/CmsPortalWeb/main/project.xhtml"
# driver = webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_ = 'shandong_zaozhuang'


def f1(driver, num):
    locator = (By.XPATH, '//tr[@height="21"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('Paging=(\d+)$', url)[0]

    if cnum != str(num):
        val = driver.find_element_by_xpath('//tr[@height="21"][1]//a').get_attribute('href')[-50:-20]

        url = url.rsplit('=', maxsplit=1)[0] + '=%s' % num
        driver.get(url)

        locator = (By.XPATH, '//tr[@height="21"][1]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find_all('tr', height='21')

    for tr in trs:
        href = tr.find('td', align='left').a['href']
        name = tr.find('td', align='left').a['title']
        ggstart_time = tr.find('td', align='right').get_text().strip()
        if 'http' in href:
            href = href
        else:
            href = 'http://www.zzztb.com' + href

        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None

    return df


def f2(driver):
    locator = (By.XPATH, '//tr[@height="21"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        total = driver.find_element_by_xpath('//div[@id="Paging"]//a[last()]').get_attribute('href')

        total = re.findall("Paging=(\d+)$", total)[0]
        total = int(total)
    except:
        total=1
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//td[@id="TDContent"][string-length()>10]')

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

    div = soup.find('td', id="TDContent").parent.parent

    return div


data = [

    ##包含招标,变更
    ["gcjs_zhaobiao_gg", "http://www.zzztb.com/front/gcxx/004001/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ###包含中标,流标
    ["gcjs_zhongbiao_gg", "http://www.zzztb.com/front/gcxx/004002/004002001/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://www.zzztb.com/front/gcxx/004002/004002002/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zgysjg_gg", "http://www.zzztb.com/front/gcxx/004002/004002004/?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],

]

def work(conp, **args):
    est_meta(conp, data=data, diqu="山东省枣庄市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "shandong_zaozhuang"])