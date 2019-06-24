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

_name_ = 'henan_kaifeng'


def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="nwes_list"]/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url

    cnum = re.findall(r'gczb/(\d+)/', url)[0]

    if cnum != str(num):
        val = driver.find_element_by_xpath('//ul[@class="nwes_list"]/li[1]//a').get_attribute('href')[-15:-5]

        url = re.sub('gczb/\d+/','gczb/%d/'%num,url)

        driver.get(url)

        locator = (By.XPATH, '//ul[@class="nwes_list"]/li[1]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find('ul', class_='nwes_list').find_all('li')
    for tr in trs:
        href = tr.find('a')['href']
        name = tr.find('a')['title']
        ggstart_time = tr.find('span',class_='date').get_text().strip('[').strip(']   ')

        if 'http' in href:
            href = href
        else:
            href = 'http://www.kfjs.gov.cn' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="nwes_list"]/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//ul[@class="pagination"]/li[last()-1]/a').get_attribute('href')
    total = re.findall('gczb/(\d+)/', total)[0]
    total = int(total)
    driver.quit()

    return total


def f3(driver, url):

    driver.get(url)

    locator = (By.XPATH,'//div[@class="ac_com"][string-length()>10]')

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

    div = soup.find('div', class_="ac_com")

    return div


data = [


    #包含中标,招标
    ["gcjs_gqita_zhao_zhong_gg", "http://www.kfjs.gov.cn/gczb/1/",[ "name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="河南省开封市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "henan_kaifeng"],headless=False,num=1)