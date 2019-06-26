import random
import pandas as pd
import re
import requests
from lxml import etree
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
from zhulong.util.etl import est_html, est_meta, add_info

_name_ = "akesu"


def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='ewb-list-items']/li[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//li[@class='active']/a")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        cnum = 1
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='ewb-list-items']/li[1]//a").get_attribute('href')[-30:]
        if 'listlast.html' in url:
            s = "/%d.html" % (num) if num > 1 else "/listlast.html"
            url = re.sub("/listlast\.html", s, url)
        elif num == 1:
            url = re.sub("/[0-9]*\.html", "/listlast.html", url)
        else:
            s = "/%d.html" % (num) if num > 1 else "/listlast.html"
            url = re.sub("/[0-9]*\.html", s, url)
        driver.get(url)
        locator = (By.XPATH, "//ul[@class='ewb-list-items']/li[1]//a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    tbody = soup.find("ul", class_='ewb-list-items')
    trs = tbody.find_all("li")
    data = []
    for tr in trs:
        a = tr.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        href = a['href'].strip()
        if 'http' in href:
            link = href
        else:
            link = 'http://218.84.219.238' + a['href'].strip()
        span = tr.find('span', class_='ewb-news-date').text.strip()
        if re.findall(r'^【(\w+)】', title):
            diqu = re.findall(r'^【(\w+)】', title)[0]
            info = json.dumps({'diqu': diqu}, ensure_ascii=False)
        else:
            info = None
        tmp = [title, span, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.XPATH, "//ul[@class='ewb-list-items']/li[last()]//a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//ul[@class='m-pagination-page']/li[last()]/a")
    num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='ewb-info-list'][string-length()>30]")
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
    div = soup.find('div', class_='ewb-info-list')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://218.84.219.238/aksggzy/jyxx/001001/001001001/listlast.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://218.84.219.238/aksggzy/jyxx/001001/001001003/listlast.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["zfcg_zhaobiao_gg",
     "http://218.84.219.238/aksggzy/jyxx/001002/001002001/listlast.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhongbiao_gg",
     "http://218.84.219.238/aksggzy/jyxx/001002/001002003/listlast.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_zhaobiao_jtgl_gg",
     "http://218.84.219.238/aksggzy/jyxx/001003/001003001/listlast.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': '交通公路'}), f2],
    #
    ["gcjs_zhongbiao_jtgl_gg",
     "http://218.84.219.238/aksggzy/jyxx/001003/001003003/listlast.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': '交通公路'}), f2],
    #
    ["gcjs_zhaobiao_shuili_gg",
     "http://218.84.219.238/aksggzy/jyxx/001004/001004001/listlast.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': '水利工程'}), f2],
    #
    ["gcjs_zhongbiao_shuili_gg",
     "http://218.84.219.238/aksggzy/jyxx/001004/001004002/listlast.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': '水利工程'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="新疆省阿克苏市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "akesu"], pageloadtimeout=120, pageLoadStrategy='none', headless=False, num=1)

    # driver=webdriver.Chrome()
    # url="http://zfcg.xjcz.gov.cn/djl/cmsPublishAction.do?method=selectCmsInfoPublishList&channelId=143"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    # driver=webdriver.Chrome()
    # url="http://zfcg.xjcz.gov.cn/djl/cmsPublishAction.do?method=selectCmsInfoPublishList&channelId=143"
    # driver.get(url)
    # for i in range(3, 5):
    #     df=f1(driver, i)
    #     print(df.values)
    #     for m in df[2].values:
    #         f = f3(driver, m)
    #         print(f)
