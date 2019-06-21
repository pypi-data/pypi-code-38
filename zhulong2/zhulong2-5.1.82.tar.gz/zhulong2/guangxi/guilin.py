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

from zhulong2.util.etl import est_html, est_meta, add_info

_name_ = "guangxi_guilin"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='column infoLink noBox unitWidth_x6']/ul/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@id='QuotaList_paginate']/span[1]")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(re.findall(r'(\d+)/', st)[0])
    except:
        cnum = 1

    if num != cnum:
        val = driver.find_element_by_xpath(
            "//div[@class='column infoLink noBox unitWidth_x6']/ul/li[1]/a").get_attribute('href')[-30:]
        driver.execute_script("pageDirection.jump('{}')".format(num))
        locator = (
        By.XPATH, "//div[@class='column infoLink noBox unitWidth_x6']/ul/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("div", class_="column infoLink noBox unitWidth_x6")
    ul = div.find('ul')
    trs = ul.find_all("li")
    data = []
    for tr in trs:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        try:
            td = tr.find('span', class_="date").text.strip()
        except:
            td = tr.find('font')['color']
            if td: td = re.findall(r'(\d+-\d+-\d+)', td)[0]
        link = 'http://zfcg.glcz.cn:880' + a['href'].strip()
        tmp = [title, td, link]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='column infoLink noBox unitWidth_x6']/ul/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@id='QuotaList_paginate']/span[1]")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = int(re.findall(r'/(\d+)', st)[0])
    except:
        num = 1
    driver.quit()
    return num


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='frameReport'][string-length()>10]")
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
    div = soup.find('div', class_='frameReport')
    return div


data = [
    ["zfcg_zhaobiao_shiji_gg",
     "http://zfcg.glcz.cn:880/CmsNewsController/getCmsNewsList/channelCode-shengji_cggg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],
    #
    ["zfcg_yucai_dyly_shiji_gg",
     "http://zfcg.glcz.cn:880/CmsNewsController/getCmsNewsList/channelCode-shengji_dylygg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'zbfs': '单一来源'}), f2],
    #
    ["zfcg_biangeng_shiji_gg",
     "http://zfcg.glcz.cn:880/CmsNewsController/getCmsNewsList/channelCode-shengji_gzgg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],
    #
    ["zfcg_gqita_zhong_liu_shiji_gg",
     "http://zfcg.glcz.cn:880/CmsNewsController/getCmsNewsList/channelCode-shengji_cjgg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'gglx': '成交公告'}), f2],
    #
    ["zfcg_zhongbiao_shiji_gg",
     "http://zfcg.glcz.cn:880/CmsNewsController/getCmsNewsList/channelCode-shengji_zbgg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],
    #
    ["zfcg_gqita_shiji_gg",
     "http://zfcg.glcz.cn:880/CmsNewsController/getCmsNewsList/channelCode-shengji_qtgg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],
    # # #
    ["zfcg_zhaobiao_xianqu_gg",
     "http://zfcg.glcz.cn:880/CmsNewsController/getCmsNewsList/channelCode-sxjcg_cggg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县区级'}), f2],
    #
    ["zfcg_yucai_dyly_xianqu_gg",
     "http://zfcg.glcz.cn:880/CmsNewsController/getCmsNewsList/channelCode-sxjcg_dylygg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县区级', 'zbfs': '单一来源'}), f2],
    # #
    ["zfcg_biangeng_xianqu_gg",
     "http://zfcg.glcz.cn:880/CmsNewsController/getCmsNewsList/channelCode-sxjcg_gzgg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县区级'}), f2],
    #
    ["zfcg_zhongbiao_xianqu_gg",
     "http://zfcg.glcz.cn:880/CmsNewsController/getCmsNewsList/channelCode-sxjcg_zbgg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县区级'}), f2],
    #
    ["zfcg_zhongbiao_lx1_xianqu_gg",
     "http://zfcg.glcz.cn:880/CmsNewsController/getCmsNewsList/channelCode-sxjcg_cjgg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县区级', 'gglx': '成交公告'}), f2],
    #
    ["zfcg_gqita_xianqu_gg",
     "http://zfcg.glcz.cn:880/CmsNewsController/getCmsNewsList/channelCode-sxjcg_qtgg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县区级'}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广西省桂林市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "guilin"])
