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

from zhulong3.util.etl import est_tbs, est_meta, est_html,est_gg

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url = "http://www.fzztb.com/CmsPortalWeb/main/project.xhtml"
# driver = webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_ = 'guangdong_shaoguan'


def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="comlist1  mt10 hx"]/li[1]/a[2]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = driver.find_element_by_xpath('//a[@class="cur"]').text

    if cnum != str(num):
        val = driver.find_element_by_xpath('//ul[@class="comlist1  mt10 hx"]/li[1]/a[2]').get_attribute('href')[-20:-2]

        if num == 1:
            url = re.sub(r'index_\d+.html', 'index.html', url)
        else:
            url = re.sub(r'index_{0,1}\d{0,}.html', 'index_%s.html' % (num - 1), url)

        driver.get(url)

        locator = (By.XPATH, '//ul[@class="comlist1  mt10 hx"]/li[1]/a[2][not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    data = []
    main_url = url.rsplit('/', maxsplit=1)[0]
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find('div', class_='gl-cont-r f-r').find('ul').find_all('li')

    for tr in trs:
        tds = tr.find_all('a')
        href = tds[1]['href'].strip('.')
        name = tds[1].get_text()
        ggstart_time = tr.span.get_text()
        if 'http' in href:
            href = href
        else:
            href = main_url + href

        tmp = [name,  ggstart_time,href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="comlist1  mt10 hx"]/li[1]/a[2]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath('//div[@class="page clearfix "]/a[last()]').get_attribute('href')
    total = re.findall("index_(\d+).html", total)[0]
    total = int(total)+1
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
                   '//div[@class="xl-cont"][string-length()>10]')

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

    div = soup.find('div', class_="xl-cont")

    return div


data = [

    #包含:招标,变更,答疑
    ["gcjs_zhaobiao_gg", "http://zgj.sg.gov.cn/xwzx/zbxx/index.html",["name", "ggstart_time", "href", "info"], f1, f2],
    #包含:中标候选,资审结果
    ["gcjs_zhongbiaohx_gg", "http://zgj.sg.gov.cn/xwzx/zbxx_7685/index.html",["name", "ggstart_time", "href", "info"], f1, f2],

]

def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省韶关市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "guangdong_shaoguan"],headless=False,num=1,pageLoadStrategy="none")