import json
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

_name_ = 'jiangsu_zhenjiang'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='ewb-main']")
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
    div = soup.find('div', class_='ewb-main')
    return div


def f1(driver, num):
    locator = (By.XPATH, "//td[@class='huifont']")
    txt = WebDriverWait(driver, 15).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall(r"(\d+)\/", txt)[0]

    if int(cnum) != int(num):
        locator = (By.XPATH, '//div[@class="ewb-right-con"]/ul/li[1]/div/a')
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-50:]
        new_url = re.sub('Paging=\d+', 'Paging=' + str(num), driver.current_url)
        driver.get(new_url)

        locator = (By.XPATH, '//div[@class="ewb-right-con"]/ul/li[1]/div/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="ewb-right-con"]/ul/li')
    for content in content_list:
        name = content.xpath("./div/a/text()")[0].strip()
        ggstart_time = content.xpath('./span[last()]/text()')[0].strip().replace('.', '-')
        href = "http://zfcg.ggzy.zhenjiang.gov.cn" + content.xpath("./div/a/@href")[0].strip()
        status = content.xpath('./span[1]/text()')[0].strip()
        area = content.xpath('./span[2]/text()')[0].strip()
        info = json.dumps({'status': status, 'area': area}, ensure_ascii=False)
        temp = [name, ggstart_time, href, info]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    # df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//td[@class='huifont']")
    txt = WebDriverWait(driver, 15).until(EC.presence_of_element_located(locator)).text
    total_page = re.findall(r"\/(\d+)", txt)[0]
    # print('total_page', total_page)
    driver.quit()

    return int(total_page)


data = [

    ["zfcg_zgys_gg",
     "http://zfcg.ggzy.zhenjiang.gov.cn/zjzc/showinfo/moreinfo_gg.aspx?categorynums=001&categorynums2=&categorynum=004001&address=001&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_dy_gg",
     "http://zfcg.ggzy.zhenjiang.gov.cn/zjzc/showinfo/moreinfo_gg.aspx?categorynums=002&categorynums2=&categorynum=004006&address=002&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_jr_gg",
     "http://zfcg.ggzy.zhenjiang.gov.cn/zjzc/showinfo/moreinfo_ggjr.aspx?categorynums=003&categorynums2=&categorynum=004006&address=003&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_yz_gg",
     "http://zfcg.ggzy.zhenjiang.gov.cn/zjzc/showinfo/moreinfo_gg.aspx?categorynums=004&categorynums2=&categorynum=004006&address=004&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_dt_gg",
     "http://zfcg.ggzy.zhenjiang.gov.cn/zjzc/showinfo/moreinfo_ggdt.aspx?categorynums=005&categorynums2=&categorynum=004006&address=005&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_xj_gg", "http://zfcg.ggzy.zhenjiang.gov.cn/zjzc/showinfo/moreinfo_gg.aspx?categorynums=&categorynums2=&categorynum=004007&address=001&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "部门(分散)采购公告"}), f2],

    ["zfcg_zhaobiao_xj_sq_gg",
     "http://zfcg.ggzy.zhenjiang.gov.cn/zjzc/showinfo/moreinfo_gg.aspx?categorynums=001&categorynums2=&categorynum=004002&address=001&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "询价公告"}), f2],
    ["zfcg_zhaobiao_xj_dy_gg",
     "http://zfcg.ggzy.zhenjiang.gov.cn/zjzc/showinfo/moreinfo_gg.aspx?categorynums=002&categorynums2=&categorynum=004002&address=002&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "询价公告"}), f2],
    ["zfcg_zhaobiao_xj_jr_gg",
     "http://zfcg.ggzy.zhenjiang.gov.cn/zjzc/showinfo/moreinfo_ggjr.aspx?categorynums=003&categorynums2=&categorynum=004002&address=003&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "询价公告"}), f2],
    ["zfcg_zhaobiao_xj_yz_gg",
     "http://zfcg.ggzy.zhenjiang.gov.cn/zjzc/showinfo/moreinfo_gg.aspx?categorynums=004&categorynums2=&categorynum=004002&address=004&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "询价公告"}), f2],
    ["zfcg_zhaobiao_xj_dt_gg",
     "http://zfcg.ggzy.zhenjiang.gov.cn/zjzc/showinfo/moreinfo_ggdt.aspx?categorynums=005&categorynums2=&categorynum=004002&address=005&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "询价公告"}), f2],

    ["zfcg_biangeng_sq_gg",
     "http://zfcg.ggzy.zhenjiang.gov.cn/zjzc/showinfo/moreinfo_gg.aspx?categorynums=001&categorynums2=&categorynum=004003&address=001&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_dy_gg",
     "http://zfcg.ggzy.zhenjiang.gov.cn/zjzc/showinfo/moreinfo_gg.aspx?categorynums=002&categorynums2=&categorynum=004003&address=002&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_jr_gg",
     "http://zfcg.ggzy.zhenjiang.gov.cn/zjzc/showinfo/moreinfo_ggjr.aspx?categorynums=003&categorynums2=&categorynum=004003&address=003&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_yz_gg",
     "http://zfcg.ggzy.zhenjiang.gov.cn/zjzc/showinfo/moreinfo_gg.aspx?categorynums=004&categorynums2=&categorynum=004003&address=004&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_dt_gg",
     "http://zfcg.ggzy.zhenjiang.gov.cn/zjzc/showinfo/moreinfo_ggdt.aspx?categorynums=005&categorynums2=&categorynum=004003&address=005&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://zfcg.ggzy.zhenjiang.gov.cn/zjzc/showinfo/moreinfo_gg.aspx?categorynums=&categorynums2=&categorynum=004008001&address=001&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_xj_gg",
     "http://zfcg.ggzy.zhenjiang.gov.cn/zjzc/showinfo/moreinfo_gg.aspx?categorynums=&categorynums2=&categorynum=004008002&address=001&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "询价"}), f2],
    ["zfcg_zhongbiao_bm_gg",
     "http://zfcg.ggzy.zhenjiang.gov.cn/zjzc/showinfo/moreinfo_gg.aspx?categorynums=&categorynums2=&categorynum=004008003&address=001&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "部门(分散)采购结果公告"}), f2],

    ["zfcg_zhongbiao_xq_dy_gg",
     "http://zfcg.ggzy.zhenjiang.gov.cn/zjzc/showinfo/moreinfo_gg.aspx?categorynums=002&categorynums2=&categorynum=004008004&address=002&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "丹阳市"}), f2],
    ["zfcg_zhongbiao_xq_jr_gg",
     "http://zfcg.ggzy.zhenjiang.gov.cn/zjzc/showinfo/moreinfo_ggjr.aspx?categorynums=003&categorynums2=&categorynum=004008004&address=003&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "句容市"}), f2],
    ["zfcg_zhongbiao_xq_yz_gg",
     "http://zfcg.ggzy.zhenjiang.gov.cn/zjzc/showinfo/moreinfo_gg.aspx?categorynums=004&categorynums2=&categorynum=004008004&address=004&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "扬中市"}), f2],
    ["zfcg_zhongbiao_xq_dt_gg",
     "http://zfcg.ggzy.zhenjiang.gov.cn/zjzc/showinfo/moreinfo_ggdt.aspx?categorynums=005&categorynums2=&categorynum=004008004&address=005&type=&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "丹徒市"}), f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="江苏省镇江市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "jiangsu_zhenjiang"],num=2)
    # driver = webdriver.Chrome()
    # driver.get( "http://zfcg.ggzy.zhenjiang.gov.cn/zjzc/showinfo/moreinfo_gg.aspx?categorynums=001&categorynums2=&categorynum=004001&address=001&type=&Paging=1")
    # for i in range(1, 5):
    #     f1(driver, 1)
    # print(f2(driver))
