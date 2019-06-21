import random
from collections import OrderedDict
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


_name_ = "shanxi_hanzhong"
start_url = None

def f1(driver, num):
    locator = (By.XPATH, "//div[@class='subright']/ul[@class='list0']/li[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//input[@id='num']")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('value').strip()
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='subright']/ul[@class='list0']/li[1]//a").get_attribute('href')[-12:]
        driver.find_element_by_xpath("//input[@id='num']").clear()
        driver.find_element_by_xpath("//input[@id='num']").send_keys(num)
        driver.execute_script('javacript:toPage()')
        locator = (By.XPATH, "//div[@class='subright']/ul[@class='list0']/li[1]//a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    divs = soup.find("div", class_="subright")
    ul = divs.find('ul', class_='list0')
    trs = ul.find_all("li")
    data = []
    for tr in trs:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        td = tr.find_all('td')[-1].text.strip()
        link = start_url+a['href'].split('./', maxsplit=1)[1]
        tmp = [title, td, link]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    global start_url
    start_url = None
    start_url = driver.current_url
    locator = (By.XPATH, "//div[@class='subright']/ul[@class='list0']/li[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='subright']/div[@style='text-align:center;']")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'共(\d+)页', st)[0]
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='subright'][string-length()>30]")
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
    div = soup.find('div', class_='subright')
    return div


data = [
    ["zfcg_zhaobiao_gk_gg",
     "http://hzcg.hanzhong.gov.cn/cggg/zbgg/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'公开'}), f2],
    #
    ["zfcg_zhaobiao_tp_gg",
     "http://hzcg.hanzhong.gov.cn/cggg/tpgg/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'谈判'}), f2],
    #
    ["zfcg_zhaobiao_cs_gg",
     "http://hzcg.hanzhong.gov.cn/cggg/csgg/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '磋商'}), f2],
    #
    ["zfcg_zhaobiao_xj_gg",
     "http://hzcg.hanzhong.gov.cn/cggg/xjgg/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '询价'}), f2],
    #
    ["zfcg_biangeng_gg",
     "http://hzcg.hanzhong.gov.cn/cggg/bjgg/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_yucai_danyilaiyuan_gg",
     "http://hzcg.hanzhong.gov.cn/cggg/fbgg/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '单一来源'}), f2],

    ###
    ["zfcg_zhongbiao_gk_gg",
     "http://hzcg.hanzhong.gov.cn/cgjg/zbgg/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhongbiao_tp_gg",
     "http://hzcg.hanzhong.gov.cn/cgjg/tpcj/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '谈判'}), f2],
    #
    ["zfcg_zhongbiao_cs_gg",
     "http://hzcg.hanzhong.gov.cn/cgjg/cgcs/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '磋商'}), f2],
    #
    ["zfcg_zhongbiao_xj_gg",
     "http://hzcg.hanzhong.gov.cn/cgjg/xjcj/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '询价'}), f2],
    #
    ["zfcg_liubiao_gg",
     "http://hzcg.hanzhong.gov.cn/cgjg/fbgg2/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhongbiao_danyilaiyuan_gg",
     "http://hzcg.hanzhong.gov.cn/cgjg/dycj/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '单一来源'}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="陕西省汉中市", **args)
    est_html(conp, f=f3, **args)


# 网站新增：http://hzcg.hanzhong.gov.cn/
# 修改时间：2019/6/20
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "hanzhong"], pageloadtimeout=120)

    # driver = webdriver.Chrome()
    # for d in data:
    #     driver.get(d[1])
    #     print(d[1])
    #     df = f2(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     df = f1(driver,1)
    #     print(df.values)
    #     for j in df[2].values:
    #         df = f3(driver, j)
    #         print(df)