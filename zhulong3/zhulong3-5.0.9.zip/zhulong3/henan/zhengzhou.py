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

from zhulong3.util.etl import est_tbs, est_meta, est_html, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url = "http://www.fzztb.com/CmsPortalWeb/main/project.xhtml"
# driver = webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_ = 'henan_zhengzhou'


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="left_picinfo_text"]//li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//ul[@class="pagination"]/li[last()-1]').text
    cnum = re.findall('第(.+?)页', cnum)[0].strip()

    if cnum != str(num):
        val = driver.find_element_by_xpath('//div[@class="left_picinfo_text"]//li[1]//a').get_attribute('href')[-30:-5]

        driver.execute_script('PageJump(%s);' % num)

        locator = (By.XPATH, '//div[@class="left_picinfo_text"]//li[1]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find('div', class_="left_picinfo_text").find_all('li')
    for tr in trs:
        tds = tr.find_all('div')
        href = tds[0].a['href']
        name = tds[0].a.get_text()
        ggstart_time = tds[1].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.zzjs.com.cn' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="left_picinfo_text"]//li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//ul[@class="pagination"]/li[last()-1]').text

    total = re.findall('共(.+?)页', total)[0].strip()

    total = int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//div[@class="main_outbor"][string-length()>10]')

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

    div = soup.find('div', class_="main_outbor")
    div.find('div',class_="location").extract()

    return div


data = [


    ["gcjs_zhaobiao_diqu1_gg", "http://www.zzjs.com.cn/Trade/TenderAnnouncement",[ "name", "ggstart_time", "href", "info"],f1, f2],
    # ["gcjs_zhaobiao_diqu2_gg", "http://www.zzjs.com.cn/Trade/CountryTenderAnnouncement",[ "name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_diqu1_gg", "http://www.zzjs.com.cn/Trade/BidPublicity",[ "name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_diqu2_gg", "http://www.zzjs.com.cn/Trade/CountryBidPublicity",[ "name", "ggstart_time", "href", "info"], f1, f2],

]


###由于diqu2数量太少,就没有划分市本级和区县

def work(conp, **args):
    est_meta(conp, data=data, diqu="河南省郑州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "henan_zhengzhou"])