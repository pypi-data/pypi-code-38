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

_name_ = 'jiangxi_nanchang'


def f1(driver, num):
    locator = (By.XPATH, '//tr[@height="30"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('Paging=(\d+)', url)[0]

    if cnum != str(num):
        val = driver.find_element_by_xpath('//tr[@height="30"][1]//a').get_attribute('href')[-30:-5]

        url = url.rsplit('=', maxsplit=1)[0] + '=%s' % num
        driver.get(url)

        locator = (By.XPATH, '//tr[@height="30"][1]//a[not(contains(@href,"%s"))]'%val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find_all('tr', height="30")

    for tr in trs:
        tds = tr.find_all('td')
        index_num = tds[0].get_text()
        name = tds[1].get_text()
        ggstart_time = tds[4].get_text()
        href = tds[5].a['href'].strip(r'../..')
        if 'http' in href:
            href = href
        else:
            href = 'http://www.ncjsztb.com/ncjsztbw/' + href
        info={'index_num':index_num}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time, href,info]

        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//tr[@height="30"][1]//a ')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//td[@class="huifont"]').text

    total = re.findall('/(\d+)$', total)[0].strip()
    total = int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//td[@id="TDContent"] | //span[@class="infodetail"]')

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

    div = soup.find('table', id="tblInfo")
    if div == None:
        div=soup.find('span',class_='infodetail')

    return div


data = [

    ["gcjs_zhaobiao_gg", "http://www.ncjsztb.com/ncjsztbw/Template/Default/zbgg_more.aspx?Paging=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ##中标公告有问题,未爬取
]

def work(conp, **args):
    est_meta(conp, data=data, diqu="江西省南昌市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "jiangxi_nanchang"])