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

from zhulong4.util.etl import est_html, est_meta, add_info,est_meta_large

_name_ = "www_sinochemitc_com"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='zbdt-news-module-content']/div[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        locator = (By.XPATH, "//span[@class='i-pager-info-c']")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='zbdt-news-module-content']/div[1]//a").get_attribute('href')[-15:]
        if num == 1:
            url = re.sub("-[0-9]*\.html", "-1.html", url)
        else:
            s = "-%d.html" % (num) if num > 1 else "-1.html"
            url = re.sub("-[0-9]*\.html", s, url)
        driver.get(url)

        locator = (By.XPATH, "//div[@class='zbdt-news-module-content']/div[1]//a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("div", class_='zbdt-news-module-content')
    lis = div.find_all('div', class_='zbdt-news-item')
    data = []
    for li in lis:
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://www.sinochemitc.com/s/' + link

        span = li.find('div', class_='zbdt-news-item-date').text.strip()
        tmp = [title, span, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='zbdt-news-module-content']/div[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//span[@class='i-pager-info-p']")
        total = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = re.findall(r'(\d+)', total)[0]
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='Gnews-detail']")
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
    div = soup.find('div', class_='Gnews-detail')
    return div



data = [
    ["qy_zhaobiao_gg",
     "http://www.sinochemitc.com/l/7239-18882-1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qy_gqita_zhong_liu_gg",
     "http://www.sinochemitc.com/l/7241-18885-1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="中国中化集团有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang3", "www_sinochemitc_com"])

    # driver = webdriver.Chrome()
    # url = "http://www.sinochemitc.com/l/7239-18882-1.html"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "http://www.sinochemitc.com/l/7239-18882-1.html"
    # driver.get(url)
    # for i in range(11, 13):
    #     df=f1(driver, i)
    #     print(df.values)
    #     for i in df[2].values:
    #         f = f3(driver, i)
    #         print(f)