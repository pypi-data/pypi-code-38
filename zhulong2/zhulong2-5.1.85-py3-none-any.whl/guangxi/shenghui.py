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

_name_ = "guangxi_shenghui"


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
        td = tr.find('span', class_="date").text.strip()
        link = 'http://222.216.4.8' + a['href'].strip()
        info = {}
        if a.find('span', class_='emLevel_0'):
            diqu1 = a.find('span', class_='emLevel_0').text.strip()
            if re.findall(r'^\[(.*)\]', diqu1):
                diqu1 = re.findall(r'^\[(.*)\]', diqu1)[0]
                diqu1 = diqu1.replace('\u3000', '')
                if diqu1: info['diqu1'] = diqu1
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:
            info = None
        tmp = [title, td, link, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
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
    div = soup.find('div', class_='frameReport')
    return div


data = [
    ["zfcg_zhaobiao_quji_gg",
     "http://222.216.4.8/CmsNewsController/getCmsNewsList/channelCode-shengji_cggg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区本级'}), f2],

    ["zfcg_yucai_dyly_quji_gg",
     "http://222.216.4.8/CmsNewsController/getCmsNewsList/channelCode-shengji_dylygg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区本级', 'zbfs': '单一来源'}), f2],

    ["zfcg_biangeng_quji_gg",
     "http://222.216.4.8/CmsNewsController/getCmsNewsList/channelCode-shengji_gzgg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区本级'}), f2],

    ["zfcg_zhongbiao_lx1_quji_gg",
     "http://222.216.4.8/CmsNewsController/getCmsNewsList/channelCode-shengji_cjgg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区本级', 'gglx': '成交公告'}), f2],

    ["zfcg_zhongbiao_quji_gg",
     "http://222.216.4.8/CmsNewsController/getCmsNewsList/channelCode-shengji_zbgg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区本级'}), f2],

    ["zfcg_gqita_zbwj_quji_gg",
     "http://222.216.4.8/CmsNewsController/getCmsNewsList/channelCode-shengji_zbwjygg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区本级', 'gglx': '招标文件预公示'}), f2],

    ["zfcg_gqita_quji_gg",
     "http://222.216.4.8/CmsNewsController/getCmsNewsList/channelCode-shengji_qtgg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区本级'}), f2],
    # #
    ["zfcg_zhaobiao_shixian_gg",
     "http://222.216.4.8/CmsNewsController/getCmsNewsList/channelCode-sxjcg_cggg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县级'}), f2],

    ["zfcg_yucai_dyly_shixian_gg",
     "http://222.216.4.8/CmsNewsController/getCmsNewsList/channelCode-sxjcg_dylygg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县级', 'zbfs': '单一来源'}), f2],
    #
    ["zfcg_gqita_zbwj_shixian_gg",
     "http://222.216.4.8/CmsNewsController/getCmsNewsList/channelCode-sxjcg_zbwjygs/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县级', 'gglx': '招标文件预公示'}), f2],
    #
    ["zfcg_biangeng_shixian_gg",
     "http://222.216.4.8/CmsNewsController/getCmsNewsList/channelCode-sxjcg_gzgg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县级'}), f2],
    #
    ["zfcg_zhongbiao_shixian_gg",
     "http://222.216.4.8/CmsNewsController/getCmsNewsList/channelCode-sxjcg_zbgg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县级'}), f2],
    #
    ["zfcg_zhongbiao_lx1_shixian_gg",
     "http://222.216.4.8/CmsNewsController/getCmsNewsList/channelCode-sxjcg_cjgg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县级', 'gglx': '成交公告'}), f2],
    #
    ["zfcg_gqita_shixian_gg",
     "http://222.216.4.8/CmsNewsController/getCmsNewsList/channelCode-sxjcg_qtgg/param_bulletin/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县级'}), f2],
    #
    ["zfcg_gqita_zhao_zhong_pljzcg_gg",
     "http://222.216.4.8/CmsNewsController/getCmsNewsList/channelCode-plzq/20/page_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市县级', 'zbfs': '批量集中采购'}), f2],
]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="广西省省会", **args)
    est_html(conp, f=f3, **args)


# f1数据太多跑不完，另外详情页一次跑不完
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "guangxi"], pageloadtimeout=120,pageLoadStrategy="none")

    # for d in data:
    #     driver=webdriver.Chrome()
    #     driver.get(d[1])
    #     df = f2(driver)
    #     print(df)
    #     driver= webdriver.Chrome()
    #     driver.get(d[1])
    #     dd = f1(driver, 3)
    #     print(dd)
