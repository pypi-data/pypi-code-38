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

from zhulong2.util.etl import est_html, est_meta, add_info, est_meta_large

_name_ = "guizhou_shenghui"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='xnrx']/ul/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//li[@class='active']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(str)
    except:
        cnum = 1

    if num != cnum:
        val = driver.find_element_by_xpath("//div[@class='xnrx']/ul/li[1]/a").get_attribute('href')[-30:]
        driver.execute_script("page({},15,'');".format(num))
        locator = (By.XPATH, "//div[@class='xnrx']/ul/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("div", class_="xnrx")
    ul = div.find('ul')
    trs = ul.find_all("li")
    data = []
    for tr in trs:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        td = tr.find('span').text.strip()
        link = 'http://www.ccgp-guizhou.gov.cn' + a['href'].strip()
        tmp = [title, td, link]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='xnrx']/ul/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='page']/ul")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = int(re.findall(r'(\d+)', str)[-2])
    except:
        num = 1
    driver.quit()
    return num


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='body'][string-length()>10]")
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
    div = soup.find('div', attrs={'style': 'xnrx'})
    return div


data = [
    ["zfcg_yucai_shengji_gg",
     "http://www.ccgp-guizhou.gov.cn/list-1153332561072666.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '省级'}), f2],
    # #
    ["zfcg_zhaobiao_shengji_gg",
     "http://www.ccgp-guizhou.gov.cn/list-1153418052184995.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '省级'}), f2],
    #
    ["zfcg_biangeng_shengji_gg",
     "http://www.ccgp-guizhou.gov.cn/list-1153454200156791.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '省级'}), f2],
    #
    ["zfcg_liubiao_shengji_gg",
     "http://www.ccgp-guizhou.gov.cn/list-1153488085289816.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '省级'}), f2],
    #
    ["zfcg_zhongbiao_shengji_gg",
     "http://www.ccgp-guizhou.gov.cn/list-1153531755759540.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '省级'}), f2],
    #
    ["zfcg_zhaobiao_dyly_shengji_gg",
     "http://www.ccgp-guizhou.gov.cn/list-1153567415242344.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '省级', 'zbfs': '单一来源'}), f2],
    #
    ["zfcg_zhongbiao_dyly_shengji_gg",
     "http://www.ccgp-guizhou.gov.cn/list-1153595823404526.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '省级', 'zbfs': '单一来源', 'gglx': '单一来源(成交)公告'}), f2],
    #
    #
    ["zfcg_zgys_shengji_gg",
     "http://www.ccgp-guizhou.gov.cn/list-1156071132711523.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '省级'}), f2],
    #
    ["zfcg_yucai_shixian_gg",
     "http://www.ccgp-guizhou.gov.cn/list-1153796890012888.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县'}), f2],
    #
    ["zfcg_zhaobiao_shixian_gg",
     "http://www.ccgp-guizhou.gov.cn/list-1153797950913584.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县'}), f2],
    #
    ["zfcg_biangeng_shixian_gg",
     "http://www.ccgp-guizhou.gov.cn/list-1153817836808214.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县'}), f2],
    #
    ["zfcg_zhongbiao_shixian_gg",
     "http://www.ccgp-guizhou.gov.cn/list-1153905922931045.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县'}), f2],
    #
    ["zfcg_liubiao_shixian_gg",
     "http://www.ccgp-guizhou.gov.cn/list-1153845808113747.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县'}), f2],
    #
    ["zfcg_zhaobiao_dyly_shixian_gg",
     "http://www.ccgp-guizhou.gov.cn/list-1153924595764135.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县', 'zbfs': '单一来源'}), f2],
    #
    ["zfcg_zhongbiao_dyly_shixian_gg",
     "http://www.ccgp-guizhou.gov.cn/list-1153937977184763.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县', 'zbfs': '单一来源', 'gglx': '单一来源(成交)公告'}), f2],
    #
    ["zfcg_zhaobiao_jkcp_gg",
     "http://www.ccgp-guizhou.gov.cn/list-1156121541491168.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '进口产品公示'}), f2],
    #
    ["zfcg_yanshou_gg",
     "http://www.ccgp-guizhou.gov.cn/list-1156161701339527.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhongbiaohx_ppp_gg",
     "http://www.ccgp-guizhou.gov.cn/list-91182367483273.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': 'PPP项目预中标公示'}), f2],
]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="贵州省省级", **args)
    est_html(conp, f=f3, **args)


# zfcg_zhaobiao_shixian_gg,zfcg_zhongbiao_shixian_gg页面多
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "guizhou"], pageloadtimeout=120)
