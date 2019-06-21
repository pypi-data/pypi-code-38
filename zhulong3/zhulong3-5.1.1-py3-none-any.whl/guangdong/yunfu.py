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

_name_ = "guangdong_yunfu"


def f1(driver, num):
    locator = (By.XPATH, "//table[@class='list_table']/tbody/tr[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall("page=([0-9]{1,})", url)[0]
    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@class='list_table']/tbody/tr[2]//a").get_attribute('href')[-30:]
        if "page" not in url:
            s = "&page=%d" % (num) if num > 1 else "&page=1"
            url = url + s
        elif num == 1:
            url = re.sub("page=[0-9]*", "page=1", url)
        else:
            s = "page=%d" % (num) if num > 1 else "page=1"
            url = re.sub("page=[0-9]*", s, url)
            # print(cnum)
        driver.get(url)
        try:
            locator = (By.XPATH, "//table[@class='list_table']/tbody/tr[2]//a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            driver.refresh()
            locator = (By.XPATH, "//table[@class='list_table']/tbody/tr[2]//a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("table", class_='list_table').tbody
    lis = div.find_all("tr")
    data = []
    for li in lis[1:]:
        try:
            a = li.find("a")
            span = li.find("th")
            tmp = [a.text.strip(), span.text.strip(), "http://yfzj.yunfu.gov.cn/" + a["href"]]
        except:
            continue
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    try:
        locator = (By.XPATH, "//table[@class='list_table']/tbody/tr[2]//a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    except:
        driver.refresh()
        locator = (By.XPATH, "//table[@class='list_table']/tbody/tr[2]//a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//ul[@class='list_page']/li[last()-2]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    li = driver.find_element_by_xpath("//ul[@class='list_page']/li[last()-2]/a").text
    total = int(li)
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='article_main_txt'][string-length()>30]")
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
    div = soup.find('div', class_="article_main_txt")
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


data = [

    ["gcjs_zhaobiao_gg", "http://yfzj.yunfu.gov.cn/List.aspx?levelid=4&classid=82&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg", "http://yfzj.yunfu.gov.cn/List.aspx?levelid=4&classid=83&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省云浮市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang2", "guangdong_yunfu"])

    # driver = webdriver.Chrome()
    # url = "http://www.yfci.gov.cn/List.aspx?levelid=4&classid=83&page=1"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "http://www.yfci.gov.cn/List.aspx?levelid=4&classid=83&page=1"
    # driver.get(url)
    # for i in range(1, 6):
    #     df=f1(driver, i)
    #     print(df.values)
