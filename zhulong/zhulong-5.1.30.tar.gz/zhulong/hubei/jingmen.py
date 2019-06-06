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

_name_ = "jingmen"


def f1(driver, num):
    locator = (By.CLASS_NAME, "wb-data-item")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    url = re.sub("Paging=[0-9]{1,}", "Paging=%d" % num, url)
    driver.get(url)

    locator = (By.CLASS_NAME, "wb-data-item")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source

    soup = BeautifulSoup(page, "lxml")

    ul = soup.find("ul", class_="wb-data-item")

    lis = ul.find_all("li", class_="wb-data-list")
    data = []
    for li in lis:
        a = li.find("a")
        span = li.find("span")
        title = a["title"]
        jytype = a.find("font").text
        href = "http://zyjy.jingmen.gov.cn" + a["href"]
        ggstart_time = span.text
        tmp = [title, ggstart_time, jytype, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.CLASS_NAME, "wb-data-item")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.CLASS_NAME, "huifont")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    td = driver.find_element_by_class_name("huifont").text
    total = td.split("/")[1]
    total = int(total)
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.CLASS_NAME, "colu-bd")

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

    div = soup.find('div', class_='colu-bd')
    # div=div.find_all('div',class_='ewb-article')[0]

    return div


data = [
    ["jqita_zhaobiao_gg", "http://zyjy.jingmen.gov.cn/Front/ShowInfo/MoreInfoListjyxx.aspx?CategoryNum=003002&Paging=1",
     ["name", "ggstart_time", "jytype", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg", "http://zyjy.jingmen.gov.cn/Front/ShowInfo/MoreInfoListjyxx.aspx?CategoryNum=003003&Paging=1",
     ["name", "ggstart_time", "jytype", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data, diqu="湖北省荆门市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "127.0.0.1", "hubei", "jingmen"])
