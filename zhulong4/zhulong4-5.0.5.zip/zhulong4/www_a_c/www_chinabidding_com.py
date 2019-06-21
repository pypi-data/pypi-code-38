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



from zhulong4.util.etl import est_tbs, est_meta, est_html

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url = "http://www.fqztb.com/Home/tenderList?index=3&type=%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE"
# driver = webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_ = 'www_chinabidding_com'


def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="as-pager-body"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//a[@class="current"]').text

    if int(cnum) != num:
        val = driver.find_element_by_xpath('//ul[@class="as-pager-body"]/li[1]/a').get_attribute('href')[-24:-5]

        driver.execute_script('searchSubmit(%s)' % num)

        locator = (By.XPATH, '//ul[@class="as-pager-body"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', class_='as-pager-body')
    trs = div.find_all('li')
    for tr in trs:
        href = tr.a['href']
        name = tr.a.h5.find_all('span')[1]['title']
        ggstart_time = tr.a.h5.find_all('span')[2].get_text().strip('发布时间：')
        strongs=tr.a.div.find_all('strong')

        address = strongs[1].get_text()
        gg_hangye = strongs[0].get_text()

        if len(strongs) == 3:
            zjly=strongs[2].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.chinabidding.com' + href

        if 'zjly' in locals():
            info = {'diqu': address, 'gg_hangye': gg_hangye,'zjly':zjly}
        else:
            info={'diqu':address,'gg_hangye':gg_hangye}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]

        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="as-pager-body"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//div[@class="as-pager-pagation"]//a[last()-1]').text

    total = int(total)

    driver.quit()

    return total

def chang_fanwei(f,num):
    def inner(*args):
        driver=args[0]
        ctext = driver.find_element_by_xpath(
            '//ul[@class="table-list-items as-index-list"]/li[2]/a[@class="tag-li on"]').text

        if ctext == '招标公告':
            val = driver.find_element_by_xpath('//ul[@class="as-pager-body"]/li[1]/a').get_attribute('href')[-24:-5]
            driver.find_element_by_xpath('//ul[@class="table-list-items as-index-list"]/li[2]/a[%s]' % num).click()
            locator = (By.XPATH, '//ul[@class="as-pager-body"]/li[1]/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*args)
    return inner



def chang_type(f,num):
    def inner(*args):
        driver=args[0]
        ctext=driver.find_element_by_xpath('//ul[@class="table-list-items as-index-list"]/li[2]/a[@class="tag-li on"]').text

        if ctext == '招标公告':
            val = driver.find_element_by_xpath('//ul[@class="as-pager-body"]/li[1]/a').get_attribute('href')[-24:-5]
            driver.find_element_by_xpath('//ul[@class="table-list-items as-index-list"]/li[2]/a[%s]' % num).click()
            locator = (By.XPATH, '//ul[@class="as-pager-body"]/li[1]/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        return f(*args)
    return inner




def f3(driver, url):

    driver.get(url)

    locator = (By.XPATH, '//div[@class="content"][string-length()>10]')

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
        if i > 10: break

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    div = soup.find('div', class_="content")

    return div


data = [
    ["qy_zhaobiao_gg", "http://www.chinabidding.com/search/proj.htm",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_biangeng_gg", "http://www.chinabidding.com/search/proj.htm",["name", "ggstart_time", "href", "info"], chang_type(f1,2), chang_type(f2,2)],
    ["qy_zhongbiaohx_gg", "http://www.chinabidding.com/search/proj.htm",["name", "ggstart_time", "href", "info"], chang_type(f1,3), chang_type(f2,3)],
    ["qy_zhongbiao_gg", "http://www.chinabidding.com/search/proj.htm",["name", "ggstart_time", "href", "info"], chang_type(f1,4), chang_type(f2,4)],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="中国国际工程咨询有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch3", "www_chinabidding_com"],headless=False,num=1)
    pass