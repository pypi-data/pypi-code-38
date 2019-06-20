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

_name_ = "yunnan_yuxi"


def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='newsList']//li[1]/p/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='fanye']//td[@align='right']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(re.findall(r'(\d+)/', st)[0])
    except:
        cnum = 1

    url = driver.current_url
    if num != cnum:
        val = driver.find_element_by_xpath("//ul[@class='newsList']//li[1]/p/a").get_attribute('href')[-15:]
        if '_' not in url:
            s = "_%d.html" % (num) if num > 1 else ".html"
            url = re.sub("\.html", s, url)
        elif num == 1:
            url = re.sub("_[0-9]*\.html", ".html", url)
        else:
            s = "_%d.html" % (num) if num > 1 else ".html"
            url = re.sub("_[0-9]*\.html", s, url)
        driver.get(url)
        locator = (By.XPATH, "//ul[@class='newsList']//li[1]/p/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    ul = soup.find("ul", class_="newsList")
    trs = ul.find_all("li")
    data = []
    for tr in trs:
        info = {}
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = tr.find('div', class_="title").text.strip()

        ggstart_time = tr.find('span', class_='fr date').text.strip()
        if re.findall(r'(\d+-\d+-\d+)', ggstart_time):
            ggstart_time = re.findall(r'(\d+-\d+-\d+)', ggstart_time)[0]
        else:
            ggstart_time = '-'

        if tr.find('p', class_='fl'):
            td = tr.find('p', class_='fl').text.strip()
            if re.findall(r'(\d+-\d+)', td):
                time = re.findall(r'(\d+-\d+)', td)[0]
                info['time'] = time
            if re.findall(r'\[(.*?)\]', td):
                diqu = re.findall(r'\[(.*?)\]', td)[0]
                if "监督公告" in diqu:
                    diqu = re.findall(r'(..县|..市)', td)[0]
                info['diqu'] = diqu
        href = a['href'].strip()
        if 'http' in href:
            link = href
        else:
            link = 'http://zfcg.yuxi.gov.cn' + href
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:
            info = None
        tmp = [title, ggstart_time, link, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, "//ul[@class='newsList']//li[1]/p/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='fanye']//td[@align='right']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = int(re.findall(r'/(\d+)', str)[0])
    except:
        num = 1
    driver.quit()
    return num


def f3(driver, url):
    driver.get(url)
    html_data = driver.page_source
    if 'Sorry, Page Not Found' in str(html_data):
        return '404'
    locator = (By.XPATH, "//div[@class='articleBox'][string-length()>10]")
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
    div = soup.find('div', class_='articleBox')
    return div


data = [
    ["zfcg_gqita_zhao_bian_gg",
     "http://zfcg.yuxi.gov.cn/channels/62.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://zfcg.yuxi.gov.cn/channels/63.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_dyly_jkcp_gg",
     "http://zfcg.yuxi.gov.cn/channels/64.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '单一来源\进口产品审核前公示'}), f2],

    ["zfcg_gqita_zhong_he_gg",
     "http://zfcg.yuxi.gov.cn/channels/65.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '采购前公示'}), f2],

    ["zfcg_gqita_zhao_zhongz_yewu_gg",
     "http://zfcg.yuxi.gov.cn/channels/55.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '业务公告'}), f2],

    ["zfcg_gqita_jiandu_gg",
     "http://zfcg.yuxi.gov.cn/channels/56.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '监督公告'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="云南省玉溪市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "yuxi"])

    # driver=webdriver.Chrome()
    # url = "http://zfcg.yuxi.gov.cn/channels/65.html"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    # driver=webdriver.Chrome()
    # url = "http://zfcg.yuxi.gov.cn/channels/65.html"
    # driver.get(url)
    # for i in range(2, 39):
    #     df=f1(driver, i)
    #     print(df.values)
    #     for i in df[2].values:
    #         f = f3(driver, i)
    #         print(f)
