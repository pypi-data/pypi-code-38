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

_name_ = "sichuan_shenghui"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='info']/ul/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='span']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(re.findall(r'(\d+)/', str)[0])
    except:
        cnum = 1

    url = driver.current_url
    if num != cnum:
        val = \
        driver.find_element_by_xpath("//div[@class='info']/ul/li[1]/a").get_attribute('href').rsplit('/', maxsplit=1)[1]
        if 'page=' not in url:
            s = "&page=%d" % (num) if num > 1 else "&page=1"
            url += s
        elif num == 1:
            url = re.sub("page=[0-9]*", "page=1", url)
        else:
            s = "page=%d" % (num) if num > 1 else "page=1"
            url = re.sub("page=[0-9]*", s, url)
        driver.get(url)
        locator = (By.XPATH, "//div[@class='info']/ul/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("div", class_="info")
    ul = div.find('ul')
    trs = ul.find_all("li")
    data = []
    for tr in trs:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = tr.find('div', class_="title").text.strip()
        td1 = tr.find('div', class_="time curr").text.strip()
        if re.findall(r'(\d+-\d+)', td1):
            td2 = re.findall(r'(\d+-\d+)', td1)[0]
        else:
            td2 = ''
        td3 = tr.find('div', class_="time curr").span.text.strip()
        td = td2 + '-' + td3
        href = a['href'].strip()
        if 'http' in href:
            link = href
        else:
            link = 'http://www.ccgp-sichuan.gov.cn' + href
        tmp = [title, td, link]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='info']/ul/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='span']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = int(re.findall(r'/(\d+)', str)[0])
    except:
        num = 1
    driver.quit()
    return num


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               "//div[@class='cont-info'][string-length()>30] | //div[@id='base_bd'][string-length()>30] | //div[@id='myPrintArea'][string-length()>30]")
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
    div = soup.find('div', class_='cont-info')
    if div == None:
        div = soup.find('div', id='base_bd')
        if div == None:
            div = soup.find('div', id='myPrintArea')
    return div


data = [
    ["zfcg_yucai_danyilaiyuan_gg",
     "http://www.ccgp-sichuan.gov.cn/CmsNewsController.do?method=recommendBulletinList&moreType=provincebuyBulletinMore&channelCode=dyly&rp=25&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '单一来源'}), f2],
    # #
    ["zfcg_yucai_jkcg_gg",
     "http://www.ccgp-sichuan.gov.cn/CmsNewsController.do?method=recommendBulletinList&moreType=provincebuyBulletinMore&channelCode=jkcg&rp=25&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '进口采购'}), f2],
    #
    ["zfcg_yucai_gg",
     "http://www.ccgp-sichuan.gov.cn/CmsNewsController.do?method=recommendBulletinList&moreType=provincebuyBulletinMore&channelCode=xqlz&rp=25&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_yanshou_gg",
     "http://www.ccgp-sichuan.gov.cn/CmsNewsController.do?method=recommendBulletinList&moreType=provincebuyBulletinMore&channelCode=lyys&rp=25&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhaobiao_shengji_gg",
     "http://www.ccgp-sichuan.gov.cn/CmsNewsController.do?method=recommendBulletinList&moreType=provincebuyBulletinMore&channelCode=cggg&rp=25&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '省级'}), f2],
    #
    ["zfcg_zhongbiao_shengji_gg",
     "http://www.ccgp-sichuan.gov.cn/CmsNewsController.do?method=recommendBulletinList&moreType=provincebuyBulletinMore&channelCode=jggg&rp=25&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '省级'}), f2],
    #
    ["zfcg_zhongbiao_lx1_shengji_gg",
     "http://www.ccgp-sichuan.gov.cn/CmsNewsController.do?method=recommendBulletinList&moreType=provincebuyBulletinMore&channelCode=cjgg&rp=25&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '省级', 'gglx': '成交公告'}), f2],
    #
    ["zfcg_biangeng_shengji_gg",
     "http://www.ccgp-sichuan.gov.cn/CmsNewsController.do?method=recommendBulletinList&moreType=provincebuyBulletinMore&channelCode=gzgg&rp=25&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '省级'}), f2],
    #
    ["zfcg_zhaobiao_jjcg_shengji_gg",
     "http://www.ccgp-sichuan.gov.cn/CmsNewsController.do?method=recommendBulletinList&moreType=provincebuyBulletinMore&channelCode=sj_jjgg&rp=25&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '省级', 'zbfs': '竞价'}), f2],
    #
    ["zfcg_zhongbiao_jjcj_shengji_gg",
     "http://www.ccgp-sichuan.gov.cn/CmsNewsController.do?method=recommendBulletinList&moreType=provincebuyBulletinMore&channelCode=sj_cjgg&rp=25&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '省级', 'zbfs': '竞价'}), f2],
    # # # #
    ["zfcg_zhaobiao_shixian_gg",
     "http://www.ccgp-sichuan.gov.cn/CmsNewsController.do?method=recommendBulletinList&moreType=provincebuyBulletinMore&channelCode=shiji_cggg&rp=25&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县'}), f2],
    # # # #
    ["zfcg_zhongbiao_shixian_gg",
     "http://www.ccgp-sichuan.gov.cn/CmsNewsController.do?method=recommendBulletinList&moreType=provincebuyBulletinMore&channelCode=shiji_jggg&rp=25&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县'}), f2],
    # # # #
    ["zfcg_zhongbiao_lx1_shixian_gg",
     "http://www.ccgp-sichuan.gov.cn/CmsNewsController.do?method=recommendBulletinList&moreType=provincebuyBulletinMore&channelCode=shiji_cjgg&rp=25&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县', 'gglx': '成交公告'}), f2],
    # # # #
    ["zfcg_liubiao_shixian_gg",
     "http://www.ccgp-sichuan.gov.cn/CmsNewsController.do?method=recommendBulletinList&moreType=provincebuyBulletinMore&channelCode=shiji_fblbgg&rp=25&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县'}), f2],
    # # # #
    ["zfcg_biangeng_shixian_gg",
     "http://www.ccgp-sichuan.gov.cn/CmsNewsController.do?method=recommendBulletinList&moreType=provincebuyBulletinMore&channelCode=shiji_gzgg&rp=25&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县'}), f2],
    # # # #
    ["zfcg_zhaobiao_jjcg_shixian_gg",
     "http://www.ccgp-sichuan.gov.cn/CmsNewsController.do?method=recommendBulletinList&moreType=provincebuyBulletinMore&channelCode=xj_jjgg&rp=25&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县', 'zbfs': '竞价'}), f2],
    # # # #
    ["zfcg_zhongbiao_jjcj_shixian_gg",
     "http://www.ccgp-sichuan.gov.cn/CmsNewsController.do?method=recommendBulletinList&moreType=provincebuyBulletinMore&channelCode=xj_cjgg&rp=25&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县', 'zbfs': '竞价'}), f2],
    # # # #
    ["zfcg_gqita_shixian_gg",
     "http://www.ccgp-sichuan.gov.cn/CmsNewsController.do?method=recommendBulletinList&moreType=provincebuyBulletinMore&channelCode=shiji_qtgg&rp=25&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="四川省省级", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "sichuan"])
