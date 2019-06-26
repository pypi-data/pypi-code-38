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

from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, add_info

_name_ = "xiangtan"


def f1(driver, num):
    locator = (By.CLASS_NAME, "text-list")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = int(re.findall("index_([0-9]{1,}).jhtml", url)[0])
    locator = (By.XPATH, "//div[@class='text-list']/ul/li[2]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    val = driver.find_element_by_xpath("//div[@class='text-list']/ul/li[2]//a").text
    if cnum != num:
        url = re.sub("(?<=index_)[0-9]{1,}(?=.jhtml)", str(num), url)
        driver.get(url)
        locator = (By.XPATH, "//div[@class='text-list']/ul/li[2]//a[string()!='%s']" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')

    ul = soup.find("div", class_="text-list")

    lis = ul.find_all("li", class_="tabletitle tabletitle2")
    data = []
    for li in lis:
        a = li.find("a")
        em = li.find("em")
        tmp = [a["title"], a.text, "https://ggzy.xiangtan.gov.cn" + a["href"], em.text.strip()]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.CLASS_NAME, "text-list")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//div[@class='text-list']/ul/li[2]//a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    info = driver.find_element_by_xpath("//div[@class='pagesite']").text
    total = re.findall("记录[\s0-9]{1,2}/([0-9]{1,})页", info)[0]
    total = int(total)
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.CLASS_NAME, "prjleft")

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

    div = soup.find('div', class_='prjleft')
    # div=div.find_all('div',class_='ewb-article')[0]

    return div


data = [["gcjs_zhaobiao_gg", "https://ggzy.xiangtan.gov.cn/zbgg/index_1.jhtml", ["name", "title", "href", "ggstart_time", "info"], f1, f2],

        ["gcjs_zhongbiaohx_gg", "https://ggzy.xiangtan.gov.cn/zbhxrgs/index_1.jhtml", ["name", "title", "href", "ggstart_time", "info"], f1, f2],

        ["gcjs_gqita_gg", "https://ggzy.xiangtan.gov.cn/zsjggs/index_1.jhtml", ["name", "title", "href", "ggstart_time", "info"], f1, f2],

        ["zfcg_zhaobiao_gg", "https://ggzy.xiangtan.gov.cn/cggg/index_1.jhtml", ["name", "title", "href", "ggstart_time", "info"], f1, f2],

        ["zfcg_biangeng_gg", "http://ggzy.xiangtan.gov.cn/gzgg/index_1.jhtml", ["name", "title", "href", "ggstart_time", "info"], f1, f2],

        ["zfcg_gqita_gg", "https://ggzy.xiangtan.gov.cn/ygg/index_1.jhtml", ["name", "title", "href", "ggstart_time", "info"], f1, f2],

        ["zfcg_zhongbiao_gg", "https://ggzy.xiangtan.gov.cn/jggg/index_1.jhtml", ["name", "title", "href", "ggstart_time", "info"], f1, f2],
        ]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖南省湘潭市", **args)
    est_html(conp, f=f3, **args)
