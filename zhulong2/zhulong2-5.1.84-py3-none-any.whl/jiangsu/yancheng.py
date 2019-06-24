import math

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

_name_ = 'jiangsu_yancheng'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//td[@height='27'and @align='center']")
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))
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
    div = soup.find('td', attrs={'align': 'center', 'height': '27'})
    return div


def f1(driver, num):
    try:
        locator = (By.XPATH, "//span[@class='default_pgStartRecord']")
        cnum_tmp = int(WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text)
        cnum = math.ceil(cnum_tmp/15)
    except:
        cnum = 1
    if int(cnum) != int(num):
        locator = (By.XPATH, "//div[@class='default_pgContainer']/table/tbody/tr[1]/td/a")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-20:]
        new_url = re.sub('pageNum=\d+', 'pageNum=' + str(num), driver.current_url)
        driver.get(new_url)

        locator = (By.XPATH, '//div[@class="default_pgContainer"]/table/tbody/tr[1]/td/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@class='default_pgContainer']/table/tbody/tr")
    for content in content_list:
        name = content.xpath("./td/a/text()")[0].strip()
        ggstart_time = content.xpath('./td[last()]/text()')[0].replace(' ','')
        href = "http://czj.yancheng.gov.cn" + content.xpath("./td/a/@href")[0].strip()
        temp = [name, ggstart_time, href]

        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    try:
        locator = (By.XPATH, "//span[@class='default_pgTotalPage']")
        total_page = int(WebDriverWait(driver, 15).until(EC.presence_of_element_located(locator)).text)
    except:
        total_page = 1
    # print('total_page', total_page)
    driver.quit()

    return int(total_page)


data = [
    # 市级
    ["zfcg_zgys_gg", "http://czj.yancheng.gov.cn/col/col20138/index.html?uid=52179&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"市级","version":"新"}), f2],
    ["zfcg_zhaobiao_gk_gg", "http://czj.yancheng.gov.cn/col/col20139/index.html?uid=52179&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"公开","area":"市级","version":"新"}), f2],
    ["zfcg_zhaobiao_tp_gg", "http://czj.yancheng.gov.cn/col/col20141/index.html?uid=52179&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"谈判","area":"市级","version":"新"}), f2],
    ["zfcg_zhaobiao_cs_gg", "http://czj.yancheng.gov.cn/col/col20142/index.html?uid=52179&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"磋商","area":"市级","version":"新"}), f2],
    ["zfcg_zhaobiao_dyly_gg", "http://czj.yancheng.gov.cn/col/col20143/index.html?uid=52179&pageNum=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"单一来源","area":"市级","version":"新"}), f2],
    ["zfcg_zhaobiao_xj_gg", "http://czj.yancheng.gov.cn/col/col20144/index.html?uid=52179&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"询价","area":"市级","version":"新"}), f2],
    ["zfcg_zhongbiao_gg", "http://czj.yancheng.gov.cn/col/col20145/index.html?uid=52179&pageNum=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"市级","version":"新"}), f2],
    ["zfcg_zhongbiao_1_gg", "http://czj.yancheng.gov.cn/col/col20146/index.html?uid=52179&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"市级","version":"新"}), f2],
    ["zfcg_liubiao_gg", "http://czj.yancheng.gov.cn/col/col20147/index.html?uid=52179&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"市级","version":"新"}), f2],
    ["zfcg_biangeng_2_gg", "http://czj.yancheng.gov.cn/col/col20148/index.html?uid=52179&pageNum=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"市级","version":"新"}), f2],
    ["zfcg_gqita_gg", "http://czj.yancheng.gov.cn/col/col20149/index.html?uid=52179&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"市级","version":"新"}), f2],


    ["zfcg_zhaobiao_gk_1_gg", "http://czj.yancheng.gov.cn/col/col20174/index.html?uid=52179&pageNum=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"公开","area":"县级","version":"新"}), f2],
    ["zfcg_zhaobiao_tp_1_gg", "http://czj.yancheng.gov.cn/col/col20176/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"谈判","area":"县级","version":"新"}), f2],
    ["zfcg_zhaobiao_cs_1_gg", "http://czj.yancheng.gov.cn/col/col20177/index.html?uid=52179&pageNum=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"磋商","area":"县级","version":"新"}), f2],

    ["zfcg_zhaobiao_dyly_1_gg", "http://czj.yancheng.gov.cn/col/col20178/index.html?uid=52179&pageNum=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"单一来源","area":"县级","version":"新"}), f2],

    ["zfcg_zhaobiao_xj_1_gg", "http://czj.yancheng.gov.cn/col/col20179/index.html?uid=52179&pageNum=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"询价","area":"县级","version":"新"}), f2],
    ["zfcg_zhongbiao_2_gg", "http://czj.yancheng.gov.cn/col/col20180/index.html?uid=52179&pageNum=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"县级","version":"新"}), f2],
    ["zfcg_zhongbiao_3_gg", "http://czj.yancheng.gov.cn/col/col20181/index.html?uid=52179&pageNum=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"县级","version":"新"}), f2],
    ["zfcg_liubiao_1_gg", "http://czj.yancheng.gov.cn/col/col20182/index.html?uid=52179&pageNum=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"县级","version":"新"}), f2],
    ["zfcg_biangeng_1_gg", "http://czj.yancheng.gov.cn/col/col20183/index.html?uid=52179&pageNum=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"县级","version":"新"}), f2],
    ["zfcg_gqita_1_gg", "http://czj.yancheng.gov.cn/col/col20184/index.html?uid=52179&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"县级","version":"新"}), f2],
    #
    #
    # # 旧系统

    ["zfcg_yucai_1_gg", "http://czj.yancheng.gov.cn/col/col2391/index.html?uid=7729&pageNum=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"市级","version":"旧"}), f2],
    ["zfcg_zhaobiao_1_gg", "http://czj.yancheng.gov.cn/col/col2392/index.html?uid=7729&pageNum=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"市级","version":"旧"}), f2],
    ["zfcg_biangeng_3_gg", "http://czj.yancheng.gov.cn/col/col2393/index.html?uid=7729&pageNum=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"市级","version":"旧"}), f2],
    ["zfcg_zhongbiao_5_gg", "http://czj.yancheng.gov.cn/col/col2394/index.html?uid=7729&pageNum=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"市级","version":"旧"}), f2],
    ["zfcg_hetong_1_gg", "http://czj.yancheng.gov.cn/col/col2395/index.html?uid=7729&pageNum=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"市级","version":"旧"}), f2],
    ["zfcg_gqita_2_gg", "http://czj.yancheng.gov.cn/col/col3329/index.html?uid=7729&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"市级","version":"旧"}), f2],
    # 旧系统

    ["zfcg_yucai_gg", "http://czj.yancheng.gov.cn/col/col2399/index.html?uid=7729&pageNum=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"县级","version":"旧"}), f2],
    ["zfcg_zhaobiao_gg", "http://czj.yancheng.gov.cn/col/col2400/index.html?uid=7729&pageNum=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"县级","version":"旧"}), f2],
    ["zfcg_biangeng_gg", "http://czj.yancheng.gov.cn/col/col2401/index.html?uid=7729&pageNum=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"县级","version":"旧"}), f2],
    ["zfcg_zhongbiao_4_gg", "http://czj.yancheng.gov.cn/col/col2402/index.html?uid=7729&pageNum=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"县级","version":"旧"}), f2],
    ["zfcg_hetong_gg", "http://czj.yancheng.gov.cn/col/col2403/index.html?uid=7729&pageNum=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"县级","version":"旧"}), f2],
]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="江苏省盐城市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "zhulong.com.cn", "192.168.169.47", "zfcg", "jiangsu_yancheng"],num=2)
    # driver = webdriver.Chrome()
    # driver.get("http://czj.yancheng.gov.cn/col/col20183/index.html?uid=52179&pageNum=2")
    # for i in range(1,5):
    #     print(f1(driver, i))
