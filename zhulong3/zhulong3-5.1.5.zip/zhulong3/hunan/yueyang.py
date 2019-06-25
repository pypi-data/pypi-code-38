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

_name_ = 'hunan_yueyang'

def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="news-list"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url

    cnum = driver.find_element_by_xpath('//div[@id="pagination"]/span[1]').text
    cnum = re.findall(r'(\d+)/', cnum)[0].strip()


    if cnum != str(num):
        val = driver.find_element_by_xpath('//ul[@class="news-list"]/li[1]/a').get_attribute('href')[-15:-5]

        if num == 1:
            url = url.rsplit('_', maxsplit=1)[0] + '.htm'
        else:
            url = re.sub(r'(_\d+.htm)|((?<!_).htm)', '_%s.htm' % str(num - 1), url)
        driver.get(url)

        locator = (By.XPATH, '//ul[@class="news-list"]/li[1]/a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []
    main_url = url.rsplit('/', maxsplit=1)[0]
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find('ul', class_='news-list').find_all('li')
    for tr in trs:
        href = tr.a['href']
        name = tr.a['title']
        ggstart_time = tr.span.get_text()

        if 'http' in href:
            href = href
        else:
            href = main_url + '/' + href
        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None

    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="news-list"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath('//div[@id="pagination"]/span[1]').text
    total = re.findall(r'/(\d+)页', total)[0].strip()
    total = int(total)
    driver.quit()

    return total


def f4(driver,num):
    locator = (By.XPATH, '//ul[@class="news-list"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url

    cnum = driver.find_element_by_xpath('//span[@class="current"]').text

    if cnum != str(num):
        val = driver.find_element_by_xpath('//ul[@class="news-list"]/li[1]/a').get_attribute('href')[-30:-5]

        if num == 1:
            url = re.sub('offset=\d+?&', 'offset=0&', url)
        else:
            url = re.sub(r'offset=\d+?&', 'offset=%s&' % str((num - 1) * 25), url)

        driver.get(url)

        locator = (By.XPATH, '//ul[@class="news-list"]/li[1]/a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []
    main_url = url.rsplit('/', maxsplit=1)[0]
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find('ul', class_='news-list').find_all('li')
    for tr in trs:
        href = tr.a['href']
        name = tr.a['title']
        ggstart_time = tr.span.get_text()

        if 'http' in href:
            href = href
        else:
            href = main_url + '/' + href
        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None

    return df


def f5(driver):
    locator = (By.XPATH, '//ul[@class="news-list"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath('//div[@class="news-right"]/span[last()-1]/a').get_attribute('href')
    total = re.findall(r'offset=(\d+?)&', total)[0].strip()
    total = int(total)//25+1
    driver.quit()

    return total



def f3(driver, url):
    driver.get(url)

    try:
        locator = (By.XPATH,'//div[@id="content"][string-length()>10]')

        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    except:
        if '404' in driver.title:
            return '404'
        else:
            raise TimeoutError

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

    div = soup.find('div', id="content")

    return div


data = [

    #包含招标,流标
    ["gcjs_zhaobiao_gg", "http://jsj.yueyang.gov.cn/54027/54028/54043/54055/index.htm",[ "name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://www.yueyang.gov.cn/jsj/54027/54028/54043/54056/index.jsp?pager.offset=0&pager.desc=false",[ "name", "ggstart_time", "href", "info"], f4, f5],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖南省岳阳市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "hunan_yueyang"])