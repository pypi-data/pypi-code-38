import json

import pandas as pd
import re

import requests
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

from zhulong2.util.etl import est_meta, est_html, add_info

_name_ = 'neimenggu_shenghui'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='center']")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
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
    div = soup.find('div', id='center')
    return div


def f1(driver, num):
    url = driver.current_url
    cnum = re.findall("byf_page=(\d+)", url)[0]

    if int(cnum) != num:
        # 替换类型
        # url = re.sub("type_name=\d+", "type_name=" + str(type_name), url)
        # 替换页码
        url = re.sub("byf_page=\d+", "byf_page=" + str(num), url)
        # 替换时间戳
        url = re.sub("_=\d+", "_=" + str(int(time.time()) * 1000), url)
        driver.get(url)
    data = []
    page = driver.page_source.encode("utf-8").decode("unicode_escape")
    # 去掉html标签   ^ 在[]是去取反的意思
    areas = re.findall(r'"ADNAME":"([^"]+?)"', page)
    names = re.findall(r'"TITLE_ALL":("[^}]+?)}', page)
    times = re.findall(r'"ENDDATE":"([^,]+),', page)
    part1_urls = re.findall(r'"wp_mark_id":"([^"]+)"', page)
    part2_urls = re.findall(r'"ay_table_tag":"([^"]+)"', page)
    categories = re.findall(r'"PURNAME":"([^"]+)"', page)

    for area, name, gg_time, part_url, part2_url, category in zip(areas, names, times, part1_urls, part2_urls,categories):
        name = name.strip('"')
        url = "http://www.nmgp.gov.cn/ay_post/post.php?" + "tb_id=" + str(part2_url) + "&p_id=" + part_url
        ggstart_time = re.findall(r"[\d-]{10,10}", gg_time)[0]
        info = json.dumps({'area':area,'category':category},ensure_ascii=False)
        temp = [name, ggstart_time, url, info]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="holder"]/a[last()-1]')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    total_page = driver.find_element_by_xpath('//div[@class="holder"]/a[last()-1]').text
    driver.quit()
    return int(total_page)


def click_gg(driver, ggtype):
    val = driver.find_element_by_xpath('//*[@id="itemContainer"]/tbody/tr[1]//a').get_attribute("href")[-30:]
    driver.find_element_by_xpath(
        '//li[1]//ul[@class="spread-item fast-nav-list fast-nav-list-2 mt mb"]/li/a[contains(string(),"%s")]' % ggtype).click()
    locator = (By.XPATH, '//table[@id="itemContainer"]//tr[1]//a[not(contains(string(),"%s"))]' % val)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))


def before(f, ggtype):
    def wrap(*args):
        driver = args[0]
        driver.get("http://www.nmgp.gov.cn/category/cggg?type_name=1")
        click_gg(driver, ggtype)
        return f(*args)

    return wrap


data = [
    #
    ["zfcg_zhaobiao_gg",
     "http://www.nmgp.gov.cn/zfcgwslave/web/index.php?r=zfcgw%2Fanndata&type_name=1&byf_page=1&fun=cggg&_=" + str(
         int(time.time() * 1000)),
     ["name", "ggstart_time", "href", "info"], f1, before(f2, "招标公告")],

    ["zfcg_biangeng_zhao_gg",
     "http://www.nmgp.gov.cn/zfcgwslave/web/index.php?r=zfcgw%2Fanndata&type_name=2&byf_page=1&fun=cggg&_=" + str(
         int(time.time() * 1000)),
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'招标更正公告'}), before(f2, "招标更正公告")],

    ["zfcg_zhongbiao_gg",
     "http://www.nmgp.gov.cn/zfcgwslave/web/index.php?r=zfcgw%2Fanndata&type_name=3&byf_page=1&fun=cggg&_=" + str(
         int(time.time() * 1000)),
     ["name", "ggstart_time", "href", "info"], f1, before(f2, "中标(成交)公告")],

    ["zfcg_biangeng_zhong_gg",
     "http://www.nmgp.gov.cn/zfcgwslave/web/index.php?r=zfcgw%2Fanndata&type_name=4&byf_page=1&fun=cggg&_=" + str(
         int(time.time() * 1000)),
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'中标(成交)更正公告'}), before(f2, "中标(成交)更正公告")],

    ["zfcg_liubiao_gg",
     "http://www.nmgp.gov.cn/zfcgwslave/web/index.php?r=zfcgw%2Fanndata&type_name=5&byf_page=1&fun=cggg&_=" + str(
         int(time.time() * 1000)),
     ["name", "ggstart_time", "href", "info"], f1, before(f2, "废标公告")],

    ["zfcg_zgysjg_gg",
     "http://www.nmgp.gov.cn/zfcgwslave/web/index.php?r=zfcgw%2Fanndata&type_name=6&byf_page=1&fun=cggg&_=" + str(
         int(time.time() * 1000)),
     ["name", "ggstart_time", "href", "info"], f1, before(f2, "资格预审公告")],

    ["zfcg_biangeng_zs_gg",
     "http://www.nmgp.gov.cn/zfcgwslave/web/index.php?r=zfcgw%2Fanndata&type_name=7&byf_page=1&fun=cggg&_=" + str(
         int(time.time() * 1000)),
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'资格预审更正公告'}), before(f2, "资格预审更正公告")],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="内蒙古", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "neimenggu"],headless=False)
