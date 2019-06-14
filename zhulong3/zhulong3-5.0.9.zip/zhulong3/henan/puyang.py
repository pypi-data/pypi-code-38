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

_name_ = 'henan_puyang'


def f1(driver, num):
    locator = (By.XPATH, '(//td[@class="aspFont1"])[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url

    cnum = re.findall(r'page=(\d+)$', url)[0]


    if cnum != str(num):
        val = driver.find_element_by_xpath('(//td[@class="aspFont1"])[1]/a').get_attribute('href')[-15:]

        url = url.rsplit('=', maxsplit=1)[0] + '=%s' % num

        driver.get(url)

        locator = (By.XPATH, '(//td[@class="aspFont1"])[1]/a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find_all('td', attrs={'class': 'aspFont1', 'width': '81%'})
    for tr in trs:
        href = tr.a['href']
        name = tr.a.get_text().strip()
        ggstart_time = tr.find_next_sibling('td', class_='aspFont1').get_text().strip('[').strip(']').strip()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.pyggzy.com/' + href
        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '(//td[@class="aspFont1"])[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('(//td[@class="aspFont1"])[last()]/font[3]').text
    total = int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//div[@class="lm_c"][string-length()>10]')

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

    div = soup.find('div', class_="lm_c")

    return div


data = [

    ["gcjs_zhaobiao_gg", "http://www.pyggzy.com/list_js.asp?class=25&page=1",[ "name", "ggstart_time", "href", "info"], f1, f2],
    ##包含中标,变更
    ["gcjs_zhongbiaohx_gg", "http://www.pyggzy.com/list.asp?class=26&page=1",[ "name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="河南省濮阳市", **args)
    est_html(conp, f=f3, **args)

if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "henan_puyang"])