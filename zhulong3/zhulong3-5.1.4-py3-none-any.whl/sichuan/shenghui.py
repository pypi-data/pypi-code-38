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
import json

import time

from zhulong3.util.etl import est_html, est_meta, add_info

_name_ = "sichuan_shenghui"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='ui newslist']/div[@class='list']/span[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    try:
        locator = (By.XPATH, '//li[@class="thisclass"]')
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='ui newslist']/div[@class='list']/span[1]/a").get_attribute('href')[-30:]

        s = Select(driver.find_element_by_xpath('//select[@name="sldd"]'))

        s.select_by_visible_text("{}".format(num))

        locator = (By.XPATH, "//div[@class='ui newslist']/div[@class='list']/span[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("div", class_='ui newslist')
    div = div.find("div", class_='list')
    lis = div.find_all("span", class_='line')
    data = []
    for li in lis:
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        span = li.find("span", class_='s-time').text.strip()
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://www.scjsztb.com' + link
        tmp = [title, span, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='ui newslist']/div[@class='list']/span[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//select[@name="sldd"]/option[last()]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    li = driver.find_element_by_xpath('//select[@name="sldd"]/option[last()]').text
    total = int(li)
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='maintext']")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

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
    div = soup.find('div', id='maintext')
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


data = [

    ["gcjs_zhaobiao_gg", "http://www.scjsztb.com/a/zhaobiaogonggao/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_zhongbiaohx_gg", "http://www.scjsztb.com/a/zhongbiaogonggao/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="四川省省会", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang2", "sichuan_shenghui"])

# 修改时间：2019/5/17
