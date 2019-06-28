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

_name_ = "hengyang"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='contentText']/ul/li/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    if "index.html" in url:
        cnum = 1
    else:
        cnum = int(re.findall("index_([0-9]{1,}).html", url)[0]) + 1
    if num != cnum:
        if num == 1:
            url = re.sub("index[_0-9]*.html", "index.html", url)
        else:
            s = "index_%d.html" % (num - 1) if num > 1 else "index.html"
            url = re.sub("index[_0-9]*.html", s, url)
        val = driver.find_element_by_xpath("//div[@class='contentText']/ul/li[1]/a").text
        driver.get(url)

        locator = (By.XPATH, "//div[@class='contentText']/ul/li[1]/a[not(contains(string(),'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source

    soup = BeautifulSoup(page, "html.parser")

    div = soup.find("div", class_="contentText")

    lis = div.find_all("li", class_="nyLine")

    data = []

    for li in lis:
        a = li.find("a")
        span = li.find("span")
        tmp = [a.text.strip(), span.text.strip(), a["href"]]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    if "clsPage" in driver.page_source:

        locator = (By.XPATH, "//div[@class='clsPage']//a[contains(string(),'尾页')]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        href = driver.find_element_by_xpath("//div[@class='clsPage']//a[contains(string(),'尾页')]").get_attribute("href")
        if "index.html" in href:
            total = 1
        else:

            total = int(re.findall("index_([0-9]{1,}).html", href)[0]) + 1

        driver.quit()
        return total
    else:
        return 1


def f3(driver, url):
    driver.get(url)

    locator = (By.CLASS_NAME, "finalContent")

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

    div = soup.find('div', class_='finalContent')
    # div=div.find_all('div',class_='ewb-article')[0]

    return div


data = [

    ["gcjs_zhaobiao_gg", "http://ggzy.hengyang.gov.cn/jyxx/jsgc/zbgg_64796/index.html", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg", "http://ggzy.hengyang.gov.cn/jyxx/jsgc/zbhxrgs_64798/index.html", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_gg", "http://ggzy.hengyang.gov.cn/jyxx/jsgc/qtgg_64799/index.html", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://ggzy.hengyang.gov.cn/jyxx/zfcg/zbgg_64800/index.html", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg", "http://ggzy.hengyang.gov.cn/jyxx/zfcg/jggs/index.html", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_gg", "http://ggzy.hengyang.gov.cn/jyxx/zfcg/qtgg_64802/index.html", ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖南省衡阳市", **args)
    est_html(conp, f=f3, **args)
