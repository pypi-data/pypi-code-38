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

_name_ = "guangxi_nanning"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='c1-body']/div[1]/div/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='pagination']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(re.findall(r'(\d+)/', str)[0])
    except:
        cnum = 1

    if num != cnum:
        val = driver.find_element_by_xpath("//div[@class='c1-body']/div[1]/div/a").get_attribute('href')[-15:]
        selector = Select(driver.find_element_by_xpath("//div[@class='pagination']/select"))
        selector.select_by_value('{}'.format(num))
        locator = (By.XPATH, "//div[@class='c1-body']/div[1]/div/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("div", class_="c1-body")
    trs = div.find_all("div", class_="c1-bline")
    data = []
    for tr in trs:
        # print(tr)
        td = tr.find('div', class_="f-right").text.strip()
        div = tr.find('div', class_='f-left')
        a = div.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        link = a['href'].strip()
        tmp = [title, td, link]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='c1-body']/div[1]/div/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='pagination']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = int(re.findall(r'/(\d+)', str)[0])
    except:
        num = 1
    driver.quit()
    return num


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH,
               "//div[@class='W980 center PaddingTop10'][string-length()>10] | //div[@class='DhSeach'][string-length()>10]")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('div', class_='W980 center PaddingTop10')
    return div


data = [
    ["zfcg_yucai_gg",
     "http://zfcg.nanning.gov.cn//cxqgsgg/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_shiji_gg",
     "http://zfcg.nanning.gov.cn//sjcggg/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市本级'}), f2],

    ["zfcg_biangeng_shiji_gg",
     "http://zfcg.nanning.gov.cn//sjbggg/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市本级'}), f2],

    ["zfcg_zhongbiao_shiji_gg",
     "http://zfcg.nanning.gov.cn//sjzbgs/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市本级'}), f2],
    #
    ["zfcg_zhaobiao_xieyi_bgdq_gg",
     "http://zfcg.nanning.gov.cn//wsjj/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '协议供货', 'gglx': '办公电器公告'}), f2],
    #
    ["zfcg_zhongbiao_bgdq_gg",
     "http://zfcg.nanning.gov.cn//jjjg/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '协议供货', 'gglx': '办公电器结果公告'}), f2],
    #
    ["zfcg_zhongbiao_danyilaiyuan001_gg",
     "http://zfcg.nanning.gov.cn//gcsgdd/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '协议供货', 'gglx': '工程施工定点'}), f2],
    #
    ["zfcg_zhongbiao_danyilaiyuan002_gg",
     "http://zfcg.nanning.gov.cn//sgjldd/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '协议供货', 'gglx': '施工监理定点'}), f2],
    #
    ["zfcg_zhongbiao_danyilaiyuan003_gg",
     "http://zfcg.nanning.gov.cn//dlgddd/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '协议供货', 'gglx': '电缆管道定点'}), f2],
    #
    ["zfcg_zhongbiao_danyilaiyuan004_gg",
     "http://zfcg.nanning.gov.cn//dqsbdd/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '协议供货', 'gglx': '电气设备定点'}), f2],
    #
    ["zfcg_zhaobiao_xieyi_dlsb_gg",
     "http://zfcg.nanning.gov.cn//dlsbcggg/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '协议供货', 'gglx': '电力设备公告'}), f2],
    #
    ["zfcg_gqita_zhong_liu_dlsb_gg",
     "http://zfcg.nanning.gov.cn//dlsbjjgg/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '协议供货', 'gglx': '电力设备结果'}), f2],
    #
    ["zfcg_zhaobiao_xianqu_gg",
     "http://zfcg.nanning.gov.cn//xqcggg/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县区级'}), f2],

    ["zfcg_biangeng_xianqu_gg",
     "http://zfcg.nanning.gov.cn//xqbggg/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县区级'}), f2],

    ["zfcg_zhongbiao_xianqu_gg",
     "http://zfcg.nanning.gov.cn//xqzbgg/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县区级'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广西省南宁市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "nanning"])
