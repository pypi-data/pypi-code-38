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
# url = "http://www.fqztb.com/Home/tenderList?index=3&type=%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE"
# driver = webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_ = 'fujian_fuqing'


def f1(driver, num):
    locator = (By.XPATH, '//ul[@id="list"]/li[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath('//span[@class="cPageNum"]').text

    if int(cnum) != num:
        val = driver.find_element_by_xpath('//ul[@id="list"]/li[2]/a').get_attribute('href').rsplit('/',maxsplit=1)[1]
        val=re.findall('&tpid=.+?&',val)
        if val:
            val=val[0]
        else:
            val='kong'

        driver.execute_script('pageNav.go(%s,%s,"pageNav");'%(num,total_page))

        # 第二个等待
        locator = (By.XPATH, '//ul[@id="list"]/li[2]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', id='list')
    trs = div.find_all('li', attrs={"class": ""})
    for tr in trs:

        href = tr.a['href']
        name = tr.a.get_text().strip()
        ggstart_time = tr.span.get_text().strip()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.fqztb.com' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)

    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    global total_page
    locator = (By.XPATH, '//ul[@id="list"]/li[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//div[@id="pageNav"]').text
    total = re.findall('共(.+?)页', total)[0].strip()

    total = int(total)
    total_page=total
    driver.quit()

    return total


def chang_type(f,num):
    def inner(*args):
        driver=args[0]
        locator = (By.XPATH, '//ul[@id="list"]/li[2]/a')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        ctext=driver.find_element_by_xpath('//button[@class="btn-site on"]').text.strip()
        if ctext == '招标公告':
            val = \
            driver.find_element_by_xpath('//ul[@id="list"]/li[2]/a').get_attribute('href').rsplit('/', maxsplit=1)[1]
            val = re.findall('&tpid=.+?&', val)
            if val:
                val = val[0]
            else:
                val = 'kong'
            driver.find_element_by_xpath('//div[@class="site-before"]/button[%d]'%num).click()

            # 第二个等待
            locator = (By.XPATH, '//ul[@id="list"]/li[2]/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*args)
    return inner


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH,
               '//div[@class="main"]')

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    driver.switch_to.frame('myFrame')

    locator = (By.XPATH,
               '//div[@class="wrap"] | //div[@id="templateContent"]')

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    locator = (By.XPATH, '//div[@class="wrap"][string-length()>200] | '
                         '//div[@id="templateContent"][string-length()>100] | '
                         '//div[@class="content"][string-length()>100]')
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

    div = soup.find('div', class_="wrap")
    if div == None:
        div=soup.find('div',id="templateContent")
        if div == None:
            div=soup.find('div',class_="content")


    driver.switch_to.parent_frame()

    return div


data = [

    ["gcjs_zhaobiao_gg", "http://www.fqztb.com/Home/tenderList?index=3&type=%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_da_bian_gg", "http://www.fqztb.com/Home/tenderList?index=3&type=%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE",["name", "ggstart_time", "href", "info"], chang_type(f1,2), chang_type(f2,2)],
    ["gcjs_gqita_da_gg", "http://www.fqztb.com/Home/tenderList?index=3&type=%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE",["name", "ggstart_time", "href", "info"], chang_type(f1,3), chang_type(f2,3)],

    ["gcjs_zhongbiaohx_gg", "http://www.fqztb.com/Home/TenderList_result?index=4&type=%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE",["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="福建省福清市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "fujian_fuqing"],headless=False,num=1)
    pass