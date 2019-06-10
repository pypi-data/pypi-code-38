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

_name_ = "zhuzhou"


def f1(driver, num):
    locator = (By.CLASS_NAME, "ewb-info-list")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = int(re.findall("([0-9]{1,}).html", url)[0])
    locator = (By.XPATH, "//ul[@class='ewb-info-list']//li[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    val = driver.find_element_by_xpath("//ul[@class='ewb-info-list']//li[1]//a").text
    if cnum != num:
        url = re.sub("[0-9]{1,}(?=.html)", str(num), url)
        driver.get(url)
        locator = (By.XPATH, "//ul[@class='ewb-info-list']//li[1]//a[string()!='%s']" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')

    ul = soup.find("ul", class_="ewb-info-list")
    lis = ul.find_all("li", class_="ewb-list-node clearfix")
    data = []
    for li in lis:
        a = li.find("a")
        span = li.find("span", recursive=False)
        tmp = [a["title"], "http://www.zzzyjy.cn" + a["href"], span.text.strip()]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.CLASS_NAME, "ewb-info-list")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    if "下页" in driver.page_source:
        locator = (By.XPATH, "//ul[@class='ewb-info-list']//li[1]//a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        total = int(driver.find_element_by_id("index").text.split("/")[1])
        driver.quit()
        return total
    else:
        driver.quit()
        return 1


def f3(driver, url):
    driver.get(url)

    locator = (By.CLASS_NAME, "ewb-detail-box")

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

    div = soup.find('div', class_='ewb-detail-box')
    div = div.find_all('div', class_='ewb-article')[0]

    return div


data = [
    ["gcjs_fangwu_zhaobiao_gg", "http://www.zzzyjy.cn/016/016001/016001001/1.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_fangwu_zhongbiaohx_gg", "http://www.zzzyjy.cn/016/016001/016001004/1.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_fangwu_zhongbiao_gg", "http://www.zzzyjy.cn/016/016001/016001006/1.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_shizheng_zhaobiao_gg", "http://www.zzzyjy.cn/016/016002/016002001/1.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_shizheng_zhongbiaohx_gg", "http://www.zzzyjy.cn/016/016002/016002004/1.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_shizheng_zhongbiao_gg", "http://www.zzzyjy.cn/016/016002/016002006/1.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_jiaotong_zhaobiao_gg", "http://www.zzzyjy.cn/016/016003/016003001/1.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_jiaotong_zhongbiaohx_gg", "http://www.zzzyjy.cn/016/016003/016003004/1.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_jiaotong_zhongbiao_gg", "http://www.zzzyjy.cn/016/016003/016003006/1.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_shuili_zhaobiao_gg", "http://www.zzzyjy.cn/016/016004/016004001/1.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_shuili_zhongbiaohx_gg", "http://www.zzzyjy.cn/016/016004/016004004/1.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_shuili_zhongbiao_gg", "http://www.zzzyjy.cn/016/016004/016004006/1.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://www.zzzyjy.cn/017/017001/1.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_zhongbiao_gg", "http://www.zzzyjy.cn/017/017003/1.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_biangeng_gg", "http://www.zzzyjy.cn/017/017002/1.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_liubiao_gg", "http://www.zzzyjy.cn/017/017004/1.html", ["name", "href", "ggstart_time", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖南省株洲市", **args)

    est_html(conp, f=f3, **args)
