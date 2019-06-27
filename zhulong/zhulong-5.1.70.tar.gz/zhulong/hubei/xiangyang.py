import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write, db_query, db_command
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from zhulong.util.etl import est_meta, est_html, add_info
import time

_name_ = "xiangyang"


def f1(driver, num):
    locator = (By.CLASS_NAME, "list-page")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    pre_url = '/'.join(driver.current_url.split("/")[:-1])
    if num != 1:
        url = pre_url + "/index_%d.shtml" % (num - 1)
    else:
        url = pre_url + "/index.shtml"
    driver.get(url)
    locator = (By.CLASS_NAME, "list-page")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    soup = BeautifulSoup(page, "lxml")

    div = soup.find("article", class_="list-page")

    lis = div.find_all("li")
    data = []
    for li in lis:
        ggstart_time = li.find('time').text
        a = li.find("a")
        name = a.text
        href = pre_url + a["href"][1:]
        tmp = [name, ggstart_time, href]
        data.append(tmp)

    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='yahoo']/a[last()]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    while driver.find_element_by_xpath("//div[@class='yahoo']/a[last()]").text == '>':
        driver.find_element_by_xpath("//div[@class='yahoo']/a[last()-1]").click()
        locator = (By.XPATH, "//div[@class='yahoo']/a[last()]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    val = driver.find_element_by_xpath("//div[@class='yahoo']/a[last()]").text
    total = int(val) + 1
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.CLASS_NAME, "news-cont")

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

    soup = BeautifulSoup(page, 'lxml')

    div = soup.find('div', class_='news-cont')
    # div=div.find_all('div',class_='ewb-article')[0]

    return div


data = [
    ["gcjs_zhaobiao_gg", "http://jyzx.xiangyang.gov.cn/jyxx/gcjs/zbgg/index.shtml", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg", "http://jyzx.xiangyang.gov.cn/jyxx/gcjs/pbjggs/index.shtml", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg", "http://jyzx.xiangyang.gov.cn/jyxx/gcjs/zbjggg/index.shtml", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://jyzx.xiangyang.gov.cn/jyxx/zfcg/cggg/index.shtml", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg", "http://jyzx.xiangyang.gov.cn/jyxx/zfcg/zbcjgg/index.shtml", ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data, diqu="湖北省襄阳市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "127.0.0.1", "hubei", "xiangyang"])
