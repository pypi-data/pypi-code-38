import math
import re

import requests
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong3.util.etl import est_html, est_meta, add_info
import time

_name_ = 'zhejiang_zhoushan'


def f1(driver, num):
    locator = (By.XPATH, '//td[@class="huifont"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//table[@class="article-body"]/tbody/tr/td/table[1]/tbody/tr[@height="30"]/td/a').get_attribute("href")[-60:]
    cnum_temp = driver.find_element_by_xpath('//td[@class="huifont"]').text
    cnum = re.findall(r'(\d+)\/',cnum_temp)[0]
    locator = (By.XPATH, '//table[@class="article-body"]/tbody/tr/td/table[1]/tbody/tr[@height="30"]')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    if int(cnum) != int(num):
        url = re.sub('Paging=\d+',"Paging="+str(num),driver.current_url)
        driver.get(url)
        locator = (
        By.XPATH, '//table[@class="article-body"]/tbody/tr/td/table[1]/tbody/tr[@height="30"]/td/a[not(contains(@href,"%s"))]' % val)
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@class="article-body"]/tbody/tr/td/table[1]/tbody/tr[@height="30"]')
    for i, content in enumerate(content_list):
        name = content.xpath("./td/a/text()")[0].strip()
        url = 'http://www.zsptztb.com.cn'+content.xpath("./td/a/@href")[0].strip()
        ggstart_time = content.xpath("./td[last()]/text()")[0].strip().strip(']').strip('[')
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print('temp', temp)
    if len(data) ==1:data.append(['凑满2条数据，可以写入数据库', '可删除', 'None'])
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//td[@class="huifont"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_temp = driver.find_element_by_xpath('//td[@class="huifont"]').text
    total_page =re.findall("\/(\d+)",total_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//table[@id="tblInfo"]')
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
    soup = BeautifulSoup(page, 'lxml')
    div = soup.find('table', id='tblInfo')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.zsptztb.com.cn/zsptztb/gcjs/010008/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_biangeng_gg",
     "http://www.zsptztb.com.cn/zsptztb/gcjs/010009/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.zsptztb.com.cn/zsptztb/gcjs/010010/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_kaibiao_gg",
     "http://www.zsptztb.com.cn/zsptztb/gcjs/010017/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_biangeng_gg",
     "http://www.zsptztb.com.cn/zsptztb/gcjs/010011/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"Tag":"中标候选人变更"}), f2],
    ["gcjs_zgysjg_gg",
     "http://www.zsptztb.com.cn/zsptztb/gcjs/010012/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_liubiao_gg",
     "http://www.zsptztb.com.cn/zsptztb/gcjs/010013/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://www.zsptztb.com.cn/zsptztb/gcjs/010015/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_xiangzhen_gg",
     "http://www.zsptztb.com.cn/zsptztb/xzjd/037001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"乡镇"}), f2],

    ["gcjs_zhongbiao_xiangzhen_gg",
     "http://www.zsptztb.com.cn/zsptztb/xzjd/037002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"乡镇"}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="浙江省舟山市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "zhejiang_zhoushan"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://www.zsptztb.com.cn/zsptztb/gcjs/010008/?Paging=1")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 10)
    # print(f2(driver))
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://www.zsptztb.com.cn//zsptztb/InfoDetail/?InfoID=c657cb46-5a8a-4d0f-beb9-9d9c367d8c18zbgg&CategoryNum=010008'))
    # driver.close()
