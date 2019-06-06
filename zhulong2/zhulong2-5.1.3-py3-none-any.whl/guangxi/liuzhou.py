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

_name_ = "guangxi_liuzhou"


def f1(driver, num):
    locator = (By.XPATH, "(//table[@width='620'])[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//table[@width='650']//td[@class='wz7']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(re.findall(r'(\d+)/', st)[0])
    except:
        cnum = 1

    url = driver.current_url
    if num != cnum:
        val = driver.find_element_by_xpath("(//table[@width='620'])[1]//a").get_attribute('href')[-10:]
        if num == 1:
            url = re.sub("page_[0-9]*", "page_1", url)
        else:
            s = "page_%d" % (num) if num > 1 else "page_1"
            url = re.sub("page_[0-9]*", s, url)
            # print(cnum)
        driver.get(url)
        locator = (By.XPATH, "(//table[@width='620'])[1]//a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find_all("table", width='620', cellpadding="6")
    data = []
    for tr in div:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        td = tr.find('td', class_="wz7", width="60").text.strip()
        href = a['href'].strip()
        href.replace(" ", '')
        link = 'http://www.zfcg.gov.cn' + href
        tmp = [title, td, link]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "(//table[@width='620'])[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//table[@width='650']//td[@class='wz7']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = int(re.findall(r'/(\d+)', str)[0])
    except:
        num = 1
    driver.quit()
    return num


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH,
               "//td[@background='../images/nybj.jpg'][string-length()>10] | //td[@background='/region/images/nybj.jpg'][string-length()>10]")
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
    div = soup.find('td', background="../images/nybj.jpg")
    if div == None:
        div = soup.find('td', background="/region/images/nybj.jpg")
    return div


data = [
    ["zfcg_gqita_yuzhaobiao_shiji_gg",
     "http://www.zfcg.gov.cn/1100/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'gglx': '预公示'}), f2],

    ["zfcg_zhaobiao_gkzb_shiji_gg",
     "http://www.zfcg.gov.cn/1101/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'zbfs': '公开'}), f2],

    ["zfcg_zhaobiao_jzzb_shiji_gg",
     "http://www.zfcg.gov.cn/1103/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'zbfs': '竞争'}), f2],

    ["zfcg_zhaobiao_xjzb_shiji_gg",
     "http://www.zfcg.gov.cn/1104/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'zbfs': '询价'}), f2],

    ["zfcg_gqita_zhao_yi_dyly_shiji_gg",
     "http://www.zfcg.gov.cn/1106/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'zbfs': '单一来源'}), f2],

    ["zfcg_zhaobiao_xyzb_shiji_gg",
     "http://www.zfcg.gov.cn/1107/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'zbfs': '协议'}), f2],

    ["zfcg_zhaobiao_ddzb_shiji_gg",
     "http://www.zfcg.gov.cn/1108/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'zbfs': '定点'}), f2],

    ["zfcg_biangeng_shiji_gg",
     "http://www.zfcg.gov.cn/1109/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],

    ["zfcg_zhaobiao_wszb_shiji_gg",
     "http://www.zfcg.gov.cn/1111/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'zbfs': '网商'}), f2],

    ["zfcg_zhaobiao_cszb_shiji_gg",
     "http://www.zfcg.gov.cn/1112/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'zbfs': '磋商'}), f2],
    # #
    ["zfcg_zhongbiao_gkjg_shiji_gg",
     "http://www.zfcg.gov.cn/1201/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'zbfs': '公开'}), f2],

    ["zfcg_zhongbiao_jzjg_shiji_gg",
     "http://www.zfcg.gov.cn/1203/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'zbfs': '竞争'}), f2],

    ["zfcg_zhongbiao_xjjg_shiji_gg",
     "http://www.zfcg.gov.cn/1204/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'zbfs': '询价'}), f2],

    ["zfcg_zhongbiao_dylyjg_shiji_gg",
     "http://www.zfcg.gov.cn/1206/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'zbfs': '单一来源'}), f2],

    ["zfcg_zhongbiao_xyjg_shiji_gg",
     "http://www.zfcg.gov.cn/1207/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'zbfs': '协议'}), f2],

    ["zfcg_zhongbiao_ddjg_shiji_gg",
     "http://www.zfcg.gov.cn/1208/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'zbfs': '定点'}), f2],

    ["zfcg_gqita_jieguobiangeng_shiji_gg",
     "http://www.zfcg.gov.cn/1209/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'gglx': '结果变更'}), f2],

    ["zfcg_zhongbiao_wsjg_shiji_gg",
     "http://www.zfcg.gov.cn/1211/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'zbfs': '网商'}), f2],

    ["zfcg_zhongbiao_csjg_shiji_gg",
     "http://www.zfcg.gov.cn/1212/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'zbfs': '磋商'}), f2],
    ####
    ["zfcg_zhaobiao_gkzb_xianji_gg",
     "http://www.zfcg.gov.cn/region/area_0/1101/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县级', 'zbfs': '公开'}), f2],

    ["zfcg_zhaobiao_jzzb_xianji_gg",
     "http://www.zfcg.gov.cn/region/area_0/1103/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县级', 'zbfs': '竞争'}), f2],

    ["zfcg_zhaobiao_xjzb_xianji_gg",
     "http://www.zfcg.gov.cn/region/area_0/1104/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县级', 'zbfs': '询价'}), f2],

    ["zfcg_zhaobiao_dylyzb_xianji_gg",
     "http://www.zfcg.gov.cn/region/area_0/1106/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县级', 'zbfs': '单一来源'}), f2],

    ["zfcg_zhaobiao_xyzb_xianji_gg",
     "http://www.zfcg.gov.cn/region/area_0/1107/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县级', 'zbfs': '协议'}), f2],

    ["zfcg_zhaobiao_ddzb_xianji_gg",
     "http://www.zfcg.gov.cn/region/area_0/1108/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县级', 'zbfs': '定点'}), f2],

    ["zfcg_biangeng_xianji_gg",
     "http://www.zfcg.gov.cn/region/area_0/1109/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县级'}), f2],

    ####
    ["zfcg_zhongbiao_gkjg_xianji_gg",
     "http://www.zfcg.gov.cn/region/area_0/1201/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县级', 'zbfs': '公开'}), f2],

    ["zfcg_zhongbiao_jzjg_xianji_gg",
     "http://www.zfcg.gov.cn/region/area_0/1203/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县级', 'zbfs': '竞争'}), f2],

    ["zfcg_zhongbiao_xjjg_xianji_gg",
     "http://www.zfcg.gov.cn/region/area_0/1204/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县级', 'zbfs': '询价'}), f2],

    ["zfcg_zhongbiao_dylyjg_xianji_gg",
     "http://www.zfcg.gov.cn/region/area_0/1206/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县级', 'zbfs': '单一来源'}), f2],

    ["zfcg_zhongbiao_xyjg_xianji_gg",
     "http://www.zfcg.gov.cn/region/area_0/1207/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县级', 'zbfs': '协议'}), f2],

    ["zfcg_zhongbiao_ddjg_xianji_gg",
     "http://www.zfcg.gov.cn/region/area_0/1208/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县级', 'zbfs': '定点'}), f2],

    ["zfcg_gqita_jieguobiangeng_xianji_gg",
     "http://www.zfcg.gov.cn/region/area_0/1209/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县级', 'gglx': '结果变更'}), f2],
    ####
    ["zfcg_zhaobiao_gkzb_chengqu_gg",
     "http://www.zfcg.gov.cn/region/area_1/1101/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '城区', 'zbfs': '公开'}), f2],

    ["zfcg_zhaobiao_jzzb_chengqu_gg",
     "http://www.zfcg.gov.cn/region/area_1/1103/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '城区', 'zbfs': '竞争'}), f2],

    ["zfcg_zhaobiao_xjzb_chengqu_gg",
     "http://www.zfcg.gov.cn/region/area_1/1104/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '城区', 'zbfs': '询价'}), f2],

    ["zfcg_zhaobiao_dylyzb_chengqu_gg",
     "http://www.zfcg.gov.cn/region/area_1/1106/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '城区', 'zbfs': '单一来源'}), f2],

    ["zfcg_zhaobiao_xyzb_chengqu_gg",
     "http://www.zfcg.gov.cn/region/area_1/1107/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '城区', 'zbfs': '协议'}), f2],

    ["zfcg_zhaobiao_ddzb_chengqu_gg",
     "http://www.zfcg.gov.cn/region/area_1/1108/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '城区', 'zbfs': '定点'}), f2],

    ["zfcg_biangeng_chengqu_gg",
     "http://www.zfcg.gov.cn/region/area_1/1109/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '城区'}), f2],
    ####
    ["zfcg_zhongbiao_gkjg_chengqu_gg",
     "http://www.zfcg.gov.cn/region/area_1/1201/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '城区', 'zbfs': '公开'}), f2],

    ["zfcg_zhongbiao_jzjg_chengqu_gg",
     "http://www.zfcg.gov.cn/region/area_1/1203/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '城区', 'zbfs': '竞争'}), f2],

    ["zfcg_zhongbiao_xjjg_chengqu_gg",
     "http://www.zfcg.gov.cn/region/area_1/1204/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '城区', 'zbfs': '询价'}), f2],

    ["zfcg_zhongbiao_dylyjg_chengqu_gg",
     "http://www.zfcg.gov.cn/region/area_1/1206/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '城区', 'zbfs': '单一来源'}), f2],

    ["zfcg_zhongbiao_xyjg_chengqu_gg",
     "http://www.zfcg.gov.cn/region/area_1/1207/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '城区', 'zbfs': '协议'}), f2],

    ["zfcg_zhongbiao_ddjg_chengqu_gg",
     "http://www.zfcg.gov.cn/region/area_1/1208/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '城区', 'zbfs': '定点'}), f2],

    ["zfcg_gqita_jieguobiangeng_chengqu_gg",
     "http://www.zfcg.gov.cn/region/area_1/1209/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '城区', 'gglx': '结果变更'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广西省柳州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "liuzhou"])
