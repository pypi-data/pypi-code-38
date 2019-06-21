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

_name_ = 'jiangxi_pingxiang'


def f1(driver, num):
    locator = (By.XPATH, '//table[@bgcolor="#FFFFFF"]//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('page=(\d+)$', url)[0]

    if cnum != str(num):
        val = driver.find_element_by_xpath('//table[@bgcolor="#FFFFFF"]//tr[1]//a').get_attribute('href')[-15:]

        url = url.rsplit('=', maxsplit=1)[0] + '=%s' % num
        driver.get(url)

        locator = (By.XPATH, '//table[@bgcolor="#FFFFFF"]//tr[1]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find('table', bgcolor="#FFFFFF").find_all('tr', attrs={"valign": ""})

    for tr in trs:
        href = tr.find('a')['href']
        name = tr.find('a').get_text()
        ggstart_time = '1'

        if 'http' in href:
            href = href
        else:
            href = 'http://www.pxszbb.cn/' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//table[@bgcolor="#FFFFFF"]//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//table[@bgcolor="#FFFFFF"]//tr[last()]').get_attribute('innerText')

    total = re.findall('/(\d+)页', total)[0].strip()
    total = int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//table[@width="967"][2][string-length()>10]')

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

    div = soup.find_all('table', width="967")[1]

    return div


data = [

    #包含招标,其他
    ["gcjs_gqita_zhao_gg", "http://www.pxszbb.cn/NewsClass.asp?BigClass=%B9%AB%B8%E6%C0%B8&SmallClass=&page=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://www.pxszbb.cn/NewsClass.asp?BigClass=%D6%D0%B1%EA%B9%AB%CA%BE&SmallClass=&page=1",["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="江西省萍乡市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "jiangxi_pingxiang"])