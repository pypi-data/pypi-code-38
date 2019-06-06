import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write, db_command, db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

import json
from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, add_info

_name_ = "huaihua"


# driver=webdriver.Chrome()

# url="""http://app.huaihua.gov.cn/hhggzyjyzx/27595/27596/27597/index.jsp?pager.offset=0&pager.desc=false"""

# driver.get(url)


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='lbcc-nr']//li[2]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = int(re.findall("ager.offset=([0-9]*)", url)[0]) / 12 + 1

    if cnum != num:
        val = driver.find_element_by_xpath("//div[@class='lbcc-nr']//li[2]//a").get_attribute("href")[-20:]
        num = (num - 1) * 12
        url = re.sub("ager.offset=[0-9]*", "ager.offset=%d" % num, url)

        driver.get(url)

        locator = (By.XPATH, "//div[@class='lbcc-nr']//li[2]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("div", class_="lbcc-nr")

    lis = div.find_all("li")
    data = []

    for li in lis:
        span = li.find("span")
        a = li.find("a")
        tmp = [a["title"], a["href"], span.text.strip()]
        data.append(tmp)

    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='lbcc-nr']//li[2]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//ul[@class='pager']/li[last()]/a[string()='尾页']")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    txt = driver.find_element_by_xpath("//ul[@class='pager']/li[last()]/a[string()='尾页']").get_attribute("href")

    total = int(re.findall("ager.offset=([0-9]*)", txt)[0])

    total = int(total / 12) + 1

    driver.quit()

    return total






def f3(driver, url):
    driver.get(url)

    locator = (By.CLASS_NAME, "xl-content")

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

    div = soup.find('div', class_='xl-content')
    # div=div.find_all('div',class_='ewb-article')[0]

    return div


data = [
    ["gcjs_zhaobiao_gg", "http://app.huaihua.gov.cn/hhggzyjyzx/27595/27596/27597/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_zhongbiao_gg", "http://app.huaihua.gov.cn/hhggzyjyzx/27595/27596/27598/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_biangeng_gg", "http://app.huaihua.gov.cn/hhggzyjyzx/27595/27596/27599/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_liubiao_gg", "http://app.huaihua.gov.cn/hhggzyjyzx/27595/27596/27600/index.jsp?pager.offset=48&pager.desc=false",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://app.huaihua.gov.cn/hhggzyjyzx/27595/27601/27602/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_zhongbiao_gg", "http://app.huaihua.gov.cn/hhggzyjyzx/27595/27601/27603/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_biangeng_gg", "http://app.huaihua.gov.cn/hhggzyjyzx/27595/27601/27604/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_liubiao_gg", "http://app.huaihua.gov.cn/hhggzyjyzx/27595/27601/27605/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "href", "ggstart_time", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp=conp, data=data, diqu="湖南省怀化市", **args)

    est_html(conp=conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "hunan", "huaihua"])
    # driver = webdriver.Chrome()
    # driver.get("http://app.huaihua.gov.cn/hhggzyjyzx/27595/27596/27600/index.jsp?pager.offset=48&pager.desc=false")
    # print(f1(driver, 2))
