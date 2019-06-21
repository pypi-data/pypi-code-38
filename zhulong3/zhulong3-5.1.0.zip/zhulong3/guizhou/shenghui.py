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

_name_ = "guizhou_shenghui"


def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='list1']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        locator = (By.XPATH, "//div[@class='text-c']/span")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='list1']/li[1]/a").get_attribute('href')[-15:]
        if num == 1:
            url = re.sub("-[0-9]*\.html", "-1.html", url)
        else:
            s = "-%d.html" % (num) if num > 1 else "-1.html"
            url = re.sub("-[0-9]*\.html", s, url)
            # print(cnum)
        driver.get(url)
        locator = (By.XPATH, "//ul[@class='list1']/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("ul", class_='list1')
    lis = div.find_all("li")
    data = []
    for li in lis[:-1]:
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        span = li.find("span").text.strip()
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://www.gzztbxh.com/' + link.split('/',maxsplit=1)[1]
        tmp = [title, span, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//ul[@class='list1']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//div[@class='text-c']/a[last()-1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    li = driver.find_element_by_xpath("//div[@class='text-c']/a[last()-1]").text
    total = int(li)
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='content']")
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
    div = soup.find('div', class_='content')
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


data = [

    ["gcjs_zhaobiao_gg", "http://www.gzztbxh.com/list-94-1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg", "http://www.gzztbxh.com/list-95-1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="贵州省省级", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang2", "guizhou_shenghui"])

    # driver = webdriver.Chrome()
    # url = "http://www.gzztbxh.com/list-95-1.html"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "http://www.gzztbxh.com/list-95-1.html"
    # driver.get(url)
    # for i in range(1, 3):
    #     df=f1(driver, i)
    #     print(df.values)
