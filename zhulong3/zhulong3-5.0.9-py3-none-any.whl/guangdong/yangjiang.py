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

import json

import time

from zhulong3.util.etl import est_html, est_meta

_name_ = "guangdong_yangjiang"


def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='news_list']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        cnum = re.findall("page/([0-9]{1,})", url)[0]
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='news_list']/li[1]/a").get_attribute('href')[-30:]
        if "page" not in url:
            s = "/page/%d" % (num) if num > 1 else "/page/1"
            url = url + s
        elif num == 1:
            url = re.sub("page/[0-9]*", "page/1", url)
        else:
            s = "page/%d" % (num) if num > 1 else "page/1"
            url = re.sub("page/[0-9]*", s, url)
            # print(cnum)
        driver.get(url)

        locator = (By.XPATH, "//ul[@class='news_list']/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("ul", class_='news_list')
    lis = div.find_all("li")
    data = []
    for li in lis:
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
            href = 'http://www.yjjs.gov.cn' + link
        tmp = [title, span, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//ul[@class='news_list']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//a[@class='page-numbers'][last()]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        li = driver.find_element_by_xpath("//a[@class='page-numbers'][last()]").text
        total = int(re.findall(r'第(\d+) 页', li)[0])
    except:
        total = 1
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='Rbox'] | //div[@id='nr'] | //div[@class='main']")
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
    div = soup.find('div', class_="Rbox")
    if div == None:
        div = soup.find('div', id='nr')
        if div == None:
            div = soup.find('div', class_='main')

    return div


data = [

    ["gcjs_zhaobiao_gg", "http://www.yjjs.gov.cn/category/zhaobiaogongshi/page/1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg", "http://www.yjjs.gov.cn/category/zhongbiaogonggao/page/1",
     ["name", "ggstart_time", "href", "info"], f1, f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省阳江市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang2", "guangdong_yangjiang"])

    # driver = webdriver.Chrome()
    # url = "http://www.yjjs.gov.cn/category/zhongbiaogonggao/page/1"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "http://www.yjjs.gov.cn/category/zhongbiaogonggao/page/1"
    # driver.get(url)
    # for i in range(1, 6):
    #     df=f1(driver, i)
    #     print(df.values)
