import json

import pandas as pd
import re
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

_name_ = 'jilin_shenghui'


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="con08_b"]')
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
    div = soup.find('div', class_='con08_b')

    return div


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="con08_a"]//li[1]//a[1]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//div[@class="con08_a"]//li[1]//a[1]').get_attribute("href")[-50:]
    cnum = re.findall('(\d+) /', driver.find_element_by_xpath("//div[@class='sub_page']/b").text)[0]

    if int(cnum) != int(num):
        url = driver.current_url
        url = re.sub("pageNo=\d+", 'pageNo=' + str(num - 1), url)
        driver.get(url)
        locator = (By.XPATH, '//div[@class="con08_a"]//li[1]//a[1][not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="con08_a"]//li')
    for content in content_list:
        name = content.xpath(".//a[1]/text()")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = "http://www.jlszfcg.gov.cn" + content.xpath(".//a[1]/@href")[0]
        temp = [name, ggstart_time, url]
        # //div[@class="con08_a"]//li[3]/div/a[1]/following-sibling::a/img/attribute::alt
        signal = content.xpath("./div/a[1]/following-sibling::a/img/attribute::alt")
        # print(signal)
        if signal != []:
            signal = "_".join(signal)
        else:
            signal = None

        temp.append(signal)
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='sub_page']/b")
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    total_page = re.findall('/ (\d+)', driver.find_element_by_xpath("//div[@class='sub_page']/b").text)[0]
    # print('total_page', total_page)
    driver.quit()
    # print(total_page)
    return int(total_page)


data = [

    ["zfcg_zhaobiao_gongkai_gg",
     "http://www.jlszfcg.gov.cn/jilin/zbxxController.form?bidWay=GKZB&declarationType=ZHAOBGG&declarationType=GSGG&pageNo=0",
     ["name", "ggstart_time", "href", "signal","info"], add_info(f1,{'method':'公开'}), f2],
    ["zfcg_zhaobiao_yaoqing_gg",
     "http://www.jlszfcg.gov.cn/jilin/zbxxController.form?bidWay=YQZB&declarationType=ZHAOBGG&declarationType=GSGG&pageNo=0",
     ["name", "ggstart_time", "href", "signal","info"], add_info(f1,{'method':'邀请'}), f2],
    ["zfcg_zhaobiao_tanpan_gg",
     "http://www.jlszfcg.gov.cn/jilin/zbxxController.form?bidWay=JZXTP&declarationType=ZHAOBGG&declarationType=GSGG&pageNo=0",
     ["name", "ggstart_time", "href", "signal","info"], add_info(f1,{'method':'谈判'}), f2],
    ["zfcg_zhaobiao_xunjia_gg",
     "http://www.jlszfcg.gov.cn/jilin/zbxxController.form?bidWay=XJCG&declarationType=ZHAOBGG&declarationType=GSGG&pageNo=0",
     ["name", "ggstart_time", "href", "signal","info"], add_info(f1,{'method':'询价'}), f2],
    ["zfcg_zhaobiao_cuoshang_gg",
     "http://www.jlszfcg.gov.cn/jilin/zbxxController.form?bidWay=JZXCS&declarationType=ZHAOBGG&declarationType=GSGG&pageNo=0",
     ["name", "ggstart_time", "href", "signal","info"], add_info(f1,{'method':'磋商'}), f2],
    ["zfcg_zhaobiao_jingjia_gg",
     "http://www.jlszfcg.gov.cn/jilin/zbxxController.form?bidWay=DZJJCG&declarationType=&pageNo=0",
     ["name", "ggstart_time", "href", "signal","info"], add_info(f1,{'method':'竞价'}), f2],
    ["zfcg_zhaobiao_danyilaiyuan_gg",
     "http://www.jlszfcg.gov.cn/jilin/zbxxController.form?bidWay=DYCGLY&declarationType=ZHAOBGG&declarationType=GSGG&pageNo=0",
     ["name", "ggstart_time", "href", "signal","info"], add_info(f1,{'method':'单一来源'}), f2],
    ["zfcg_zhaobiao_zhengqiu_gg",
     "http://www.jlszfcg.gov.cn/jilin/zbxxController.form?bidWay=&declarationType=ZQYJGG&pageNo=0",
     ["name", "ggstart_time", "href", "signal","info"], add_info(f1,{'method':'征求'}), f2],
]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="吉林省", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "jilin"], pageloadtimeout=60,
         pageloadstrategy='none')
    # url = "http://www.jlszfcg.gov.cn/jilin/zbxxController.form?bidWay=GKZB&declarationType=ZHAOBGG&declarationType=GSGG&pageNo=0"
    # driver = webdriver.Chrome()
    # driver.get(url)
    # # # print(f2(driver))
    # print(f1(driver, 201))
    # print(f1(driver, 5))
    # driver.quit()
