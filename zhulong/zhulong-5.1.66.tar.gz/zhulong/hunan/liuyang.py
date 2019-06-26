import pandas as pd
import re

from lxml import etree
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

from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html,add_info

_name_ = "liuyang"


def f1(driver, num):
    locator = (By.ID, "list")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    if "index" not in url:
        cnum = int(re.findall("([0-9]{1,}).html", url)[0])
    else:
        cnum = 1
    locator = (By.XPATH, '//div[@id="list"]//ul/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath("//div[@id='list']//ul/li[1]/a").get_attribute("href")[-40:]
    if cnum != num:
        url = re.sub("([0-9]{1,})\.", str(num) + ".", url)
        driver.get(url)
        locator = (By.XPATH, "//div[@id='list']//ul/li[1]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    body = etree.HTML(page)
    data = []
    content_list = body.xpath("//div[@id='list']//ul/li")

    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = "http://www.liuyang.gov.cn" + content.xpath("./a/@href")[0].strip()
        tmp = [name, ggstart_time, url]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.ID, "list")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    if "下一页" in driver.page_source:
        locator = (By.XPATH, "//div[@class='page_num']/a[contains(string(),'/')]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        total = int(
            driver.find_element_by_xpath("//div[@class='page_num']/a[contains(string(),'/')]").text.split("/")[1])
        driver.quit()
        return total
    else:
        driver.quit()
        return 1


def f3(driver, url):
    driver.get(url)

    locator = (By.CLASS_NAME, "layout")

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
    div = soup.find('div', class_='layout')
    return div


data = [
    ["gcjs_fangjianshizhe_zhaobiao_gg",
     "http://www.liuyang.gov.cn/liuyanggov/dwzt/ggzyjyzx/jyxx96/fjsz34/zbgg97/2a7bc3f8-1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"gctype":"房屋建设"}), f2],
    ["gcjs_fangjianshizhe_zhongbiaohx_gg",
     "http://www.liuyang.gov.cn/liuyanggov/dwzt/ggzyjyzx/jyxx96/fjsz34/zbgs84/93281bb4-1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"gctype":"房屋建设"}), f2],

    ["gcjs_jiaotong_zhaobiao_gg",
     "http://www.liuyang.gov.cn/liuyanggov/dwzt/ggzyjyzx/jyxx96/jtgc45/zbgg57/d5605162-1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"gctype":"交通"}), f2],
    ["gcjs_jiaotong_zhongbiaohx_gg",
     "http://www.liuyang.gov.cn/liuyanggov/dwzt/ggzyjyzx/jyxx96/jtgc45/zbgs4/d26b20b2-1.html",
     ["name", "ggstart_time", "href", "info"],  add_info(f1,{"gctype":"交通"}), f2],

    ["gcjs_shuili_zhaobiao_gg", "http://www.liuyang.gov.cn/liuyanggov/dwzt/ggzyjyzx/jyxx96/slgc0/zbgg50/index.html",
     ["name", "ggstart_time", "href", "info"],  add_info(f1,{"gctype":"水利"}), f2],
    ["gcjs_shuili_zhongbiaohx_gg", "http://www.liuyang.gov.cn/liuyanggov/dwzt/ggzyjyzx/jyxx96/slgc0/zbgs91/index.html",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{"gctype":"水利"}), f2],

    ["zfcg_zhaobiao_gg", "http://www.liuyang.gov.cn/liuyanggov/dwzt/ggzyjyzx/jyxx96/zfcg90/zbgg96/8b7cf27b-1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://www.liuyang.gov.cn/liuyanggov/dwzt/ggzyjyzx/jyxx96/zfcg90/zbgs99/09c37cb5-1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖南省浏阳市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "hunan", "liuyang"])



