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

from zhulong3.util.etl import est_html, est_meta, add_info

_name_ = "ningxia_shenghui"


def f1(driver, num):
    locator = (By.XPATH, "//pre[string-length()>100]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall(r'page=(\d+)', url)[0]
    if num != int(cnum):
        html_data = driver.find_element_by_xpath('//pre').text.strip()
        html_data = json.loads(html_data)
        page = html_data['data']
        val1 = page[0]['id']
        if num == 1:
            url = re.sub("page=[0-9]*", "page=1", url)
        else:
            s = "page=%d" % (num) if num > 1 else "page=1"
            url = re.sub("page=[0-9]*", s, url)
            # print(cnum)
        driver.get(url)
        locator = (By.XPATH, "//pre[string-length()>100]")
        html_data = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        html_data = json.loads(html_data)
        page = html_data['data']
        val2 = page[0]['id']
        if val1 == val2:
            raise TimeoutError

    html_data = driver.find_element_by_xpath('//pre').text.strip()
    html_data = json.loads(html_data)
    page = html_data['data']
    data = []
    for li in page:
        if 'resid=IDJ0APFF17' in url:
            title = li['bid_title']
            try:
                span = li['bid_date']
            except:
                span = li['cdate']
            link = 'http://218.95.173.11:8091/jzptweb/bid_detail.html?id=' + li['id']
            dd = li['bid_unit_name']
            info = json.dumps({'zbdw':dd}, ensure_ascii=False)
        elif 'resid=IDJ04PPS59' in url:
            title = li['wpb_title']
            span = li['wpb_pdate']
            link = 'http://218.95.173.11:8091/jzptweb/bnotice_detail.html?id=' + li['id']
            info = None
        elif 'resid=IDJ07FIHBM' in url:
            title = li['pbid_title']
            span = li['pbid_date']
            link = 'http://218.95.173.11:8091/jzptweb/pbid_detail.html?id=' + li['id']
            info = None
        tmp = [title, span, link, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, "//pre")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    html_data = driver.find_element_by_xpath('//pre').text.strip()
    html_data = json.loads(html_data)
    total = html_data['datax']
    if int(total)/10 == int(int(total)/10):
        num = int(int(total)/10)
    else:
        num = int(int(total)/10) + 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='tab-pane active']")
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
    div = soup.find('div', class_='tab-pane active')
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


data = [
    ["gcjs_zhaobiao_diqu1_gg",
     "http://218.95.173.11:8091/selectact/query.jspx?page=1&resid=IDJ04PPS59&wpb_region=640000&rows=10",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'diqu':'区重点'}), f2],

    ["gcjs_zhaobiao_diqu2_gg",
     "http://218.95.173.11:8091/selectact/query.jspx?page=1&resid=IDJ04PPS59&wpb_region=640100&rows=10",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'diqu':'银川市'}), f2],

    ["gcjs_zhaobiao_diqu3_gg",
     "http://218.95.173.11:8091/selectact/query.jspx?page=1&resid=IDJ04PPS59&wpb_region=640400&rows=10",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'diqu':'固原市'}), f2],

    ["gcjs_zhaobiao_diqu4_gg",
     "http://218.95.173.11:8091/selectact/query.jspx?page=1&resid=IDJ04PPS59&wpb_region=640300&rows=10",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'diqu':'吴忠市'}), f2],

    ["gcjs_zhaobiao_diqu5_gg",
     "http://218.95.173.11:8091/selectact/query.jspx?page=1&resid=IDJ04PPS59&wpb_region=640500&rows=10",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'diqu':'中卫市'}), f2],

    ["gcjs_zhongbiaohx_diqu1_gg",
     "http://218.95.173.11:8091/selectact/query.jspx?page=1&resid=IDJ07FIHBM&pbid_area_code=640000&rows=10",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'diqu':'区重点'}), f2],

    ["gcjs_zhongbiaohx_diqu2_gg",
     "http://218.95.173.11:8091/selectact/query.jspx?page=1&resid=IDJ07FIHBM&pbid_area_code=640100&rows=10",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'diqu':'银川市'}), f2],

    ["gcjs_zhongbiaohx_diqu3_gg",
     "http://218.95.173.11:8091/selectact/query.jspx?page=1&resid=IDJ07FIHBM&pbid_area_code=640400&rows=10",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'diqu':'固原市'}), f2],

    ["gcjs_zhongbiaohx_diqu4_gg",
     "http://218.95.173.11:8091/selectact/query.jspx?page=1&resid=IDJ07FIHBM&pbid_area_code=640300&rows=10",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'diqu':'吴忠市'}), f2],

    ["gcjs_zhongbiaohx_diqu5_gg",
     "http://218.95.173.11:8091/selectact/query.jspx?page=1&resid=IDJ07FIHBM&pbid_area_code=640500&rows=10",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'diqu':'中卫市'}), f2],


    ["gcjs_zhongbiao_diqu1_gg",
     "http://218.95.173.11:8091/selectact/query.jspx?page=1&resid=IDJ0APFF17&bid_area_code=640000&rows=10",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'diqu':'区重点'}), f2],

    ["gcjs_zhongbiao_diqu2_gg",
     "http://218.95.173.11:8091/selectact/query.jspx?page=1&resid=IDJ0APFF17&bid_area_code=640100&rows=10",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'diqu':'银川市'}), f2],

    ["gcjs_zhongbiao_diqu3_gg",
     "http://218.95.173.11:8091/selectact/query.jspx?page=1&resid=IDJ0APFF17&bid_area_code=640400&rows=10",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'diqu':'固原市'}), f2],

    ["gcjs_zhongbiao_diqu4_gg",
     "http://218.95.173.11:8091/selectact/query.jspx?page=1&resid=IDJ0APFF17&bid_area_code=640300&rows=10",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'diqu':'吴忠市'}), f2],

    ["gcjs_zhongbiao_diqu5_gg",
     "http://218.95.173.11:8091/selectact/query.jspx?page=1&resid=IDJ0APFF17&bid_area_code=640500&rows=10",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu':'中卫市'}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="宁夏省省会", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang2", "ningxia_shenghui"])

    # driver = webdriver.Chrome()
    # url = "http://218.95.173.11:8091/selectact/query.jspx?page=1&resid=IDJ0APFF17&bid_area_code=640400&rows=10"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "http://218.95.173.11:8091/selectact/query.jspx?page=1&resid=IDJ0APFF17&bid_area_code=640400&rows=10"
    # driver.get(url)
    # for i in range(332, 333):
    #     df=f1(driver, i)
    #     print(df.values)
