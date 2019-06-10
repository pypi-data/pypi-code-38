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

from zhulong3 .util.etl import est_tbs, est_meta, est_html

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url = "http://www.fzztb.com/CmsPortalWeb/main/project.xhtml"
# driver = webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_ = 'fujian_zhangzhou'


def f1(driver, num):

    locator = (By.XPATH, '//ul[@class="news-list"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('page=(\d+)$', url)[0]

    if cnum != str(num):
        val = driver.find_element_by_xpath('//ul[@class="news-list"]/li[1]/a').get_attribute('href')[-30:-5]

        url = url.rsplit('=', maxsplit=1)[0] + '=%s' % num
        driver.get(url)

        locator = (By.XPATH, '//ul[@class="news-list"]/li[1]/a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find('ul', class_="news-list").find_all('li')

    for tr in trs:
        mark=tr.find('a')
        if not mark:
            continue

        href = tr.a['href']
        name = tr.a.get_text().strip()
        ggstart_time = tr.span.get_text()
        if 'http' in href:
            href = href
        else:
            href = 'http://jsj.zhangzhou.gov.cn' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="news-list"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//div[@class="pg2"]/a[last()-1]').get_attribute('href')

    total = re.findall('page=(\d+)$', total)[0].strip()

    total = int(total)

    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)


    locator = (By.XPATH,
               '//div[@id="Zoom"][string-length()>10]')

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

    div = soup.find('div', id="Zoom")



    return div


data = [
    ##包含招标,变更
    ["gcjs_zhaobiao_gg", "http://jsj.zhangzhou.gov.cn/cms/sitemanage/applicationIndex.shtml?applicationName=zzzjj&pageName=biddingNoticeList&siteId=530418345107680000&page=1",["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_da_bian_gg", "http://jsj.zhangzhou.gov.cn/cms/sitemanage/applicationIndex.shtml?applicationName=zzzjj&pageName=biddingQuestionList&siteId=530418345107680000&page=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_kongzhijia_gg", "http://jsj.zhangzhou.gov.cn/cms/sitemanage/applicationIndex.shtml?applicationName=zzzjj&pageName=biddingPriceList&siteId=530418345107680000&page=1",["name", "ggstart_time", "href", "info"], f1, f2],
    # 包含中标,中标候选
    ["gcjs_zhongbiaohx_gg", "http://jsj.zhangzhou.gov.cn/cms/sitemanage/applicationIndex.shtml?applicationName=zzzjj&pageName=biddingWinList&siteId=530418345107680000&page=1",["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="福建省漳州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "fujian_zhangzhou"],headless=False,cdc_total=1)