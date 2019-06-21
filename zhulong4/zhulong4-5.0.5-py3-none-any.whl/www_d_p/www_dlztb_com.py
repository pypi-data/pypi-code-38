import pandas as pd
import re

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

from zhulong4.util.etl import est_html, est_meta, add_info

_name_ = "www_dlztb_com"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='catlist']/ul/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        cnum = int(re.findall(r'_(\d+)\.html', url)[0])
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='catlist']/ul/li[1]/a").get_attribute('href')[-15:]
        tar = driver.find_element_by_xpath("//div[@class='catlist']/ul/li[last()]/a").get_attribute('href')[-15:]
        if num == 1:
            url = re.sub("_[0-9]*\.html", "_1.html", url)
        else:
            s = "_%d.html" % (num) if num > 1 else "_1.html"
            url = re.sub("_[0-9]*\.html", s, url)
        driver.get(url)

        locator = (By.XPATH, "//div[@class='catlist']/ul/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, "//div[@class='catlist']/ul/li[last()]/a[not(contains(@href, '%s'))]" % tar)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("div", class_='catlist').ul
    lis = div.find_all('li', class_='')
    data = []
    for li in lis:
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://www.dlztb.com/' + link
        span = li.find('i').text.strip()
        tmp = [title, span, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='catlist']/ul/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='pages']/cite")
        total = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = re.findall(r'/(\d+)', total)[0]
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='m3l']")
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
    div = soup.find('div', class_='m3l')
    return div



data = [
    ["qy_zhaobiao_zmzb_gg",
     "http://www.dlztb.com/news/135_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '中煤招标'}), f2],

    ["qy_zhaobiao_gjdt_gg",
     "http://www.dlztb.com/news/18_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu': '国家电投'}), f2],

    ["qy_zhaobiao_guodianzb_gg",
     "http://www.dlztb.com/news/19_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '国电招标'}), f2],

    ["qy_zhaobiao_henengzb_gg",
     "http://www.dlztb.com/news/20_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '核能招标'}), f2],

    ["qy_zhaobiao_guohuazb_gg",
     "http://www.dlztb.com/news/127_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '国华招标'}), f2],

    ["qy_zhaobiao_gjnyzb_gg",
     "http://www.dlztb.com/news/128_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '国家能源招标网'}), f2],

    ["qy_zhaobiao_guotouzb_gg",
     "http://www.dlztb.com/news/129_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '国投招标'}), f2],

    ["qy_zhaobiao_shenhuazb_gg",
     "http://www.dlztb.com/news/130_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '神华招标网'}), f2],

    ["qy_zhaobiao_bjny_gg",
     "http://www.dlztb.com/news/131_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '北京能源'}), f2],

    ["qy_zhaobiao_datangzb_gg",
     "http://www.dlztb.com/news/132_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '大唐招标'}), f2],

    ["qy_zhaobiao_zhenengzb_gg",
     "http://www.dlztb.com/news/133_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '浙能招标'}), f2],

    ["qy_zhaobiao_huadianzb_gg",
     "http://www.dlztb.com/news/134_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '华电招标'}), f2],

    ["qy_zhaobiao_guowangzb_gg",
     "http://www.dlztb.com/news/136_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '国网招标'}), f2],

    ["qy_zhaobiao_huannengzb_gg",
     "http://www.dlztb.com/news/137_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '华能招标'}), f2],

    ["qy_zhaobiao_nanwangzb_gg",
     "http://www.dlztb.com/news/138_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '南网招标'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="中国中煤能源集团有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang3", "www_dlztb_com"])

# 修改时间：2019/5/17
