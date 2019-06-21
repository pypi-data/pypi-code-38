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

_name_ = 'shanxi1_taiyuan'


def f1(driver, num):
    locator = (By.ID, "pages")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    cnum = int(driver.find_element_by_xpath("//span[@class='active']").text)
    locator = (By.XPATH, "//div[@class='list_service']/table/tbody/tr")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//div[@class='list_service']/table/tbody/tr[1]/td/dl/dt/a").get_attribute("href")[-20:]
    if int(cnum) != int(num):
        url = re.sub(r"index[_\d]{0,5}\.shtml","%s%s.shtml"%('index_' if str(num)!='1' else 'index',str(num) if str(num)!='1' else ''),driver.current_url)
        # print(url)
        driver.get(url)
        locator = (By.XPATH, '//div[@class="list_service"]/table/tbody/tr[1]/td/dl/dt/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='list_service']/table/tbody/tr")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@class='list_service']/table/tbody/tr")
    for content in content_list:
        name = content.xpath("./td/dl/dt/a/text()")[0].strip()
        ggstart_time = content.xpath("./td[2]/text()")[0].strip()
        url = 'http://zjw.taiyuan.gov.cn'+content.xpath("./td/dl/dt/a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//*[@id="pages"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_page = driver.execute_script("return pageCount;")
    if ',' in total_page:total_page = total_page.split(',')[1]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    time.sleep(0.1)
    locator = (By.XPATH, "//div[@class='mainCont']")
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
    div = soup.find('div', class_='mainCont')
    return div


data = [
    # ["gcjs_buyi_sg_gg",
    #  "http://zjw.taiyuan.gov.cn/ggfw/bmfwcxl/bytz/sg/index.shtml", #992
    #  ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'施工'}), f2],

    ["gcjs_zhongbiao_sg_gg",
     "http://zjw.taiyuan.gov.cn/ggfw/bmfwcxl/zbgs/sg/index.shtml", #992
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'施工'}), f2],

    ["gcjs_zhaobiao_sg_gg",
     "http://zjw.taiyuan.gov.cn/ggfw/bmfwcxl/zbgg/sg/index.shtml", #992
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'施工'}), f2],

    ["gcjs_kongzhijia_sg_gg",
     "http://zjw.taiyuan.gov.cn/ggfw/bmfwcxl/kzjgs/sg/index.shtml", #992
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'施工'}), f2],

    ["gcjs_zhaobiao_jl_gg",
     "http://zjw.taiyuan.gov.cn/ggfw/bmfwcxl/zbgg/jl/index.shtml",  #97
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'监理'}), f2],

    ["gcjs_zhongbiao_jl_gg",
     "http://zjw.taiyuan.gov.cn/ggfw/bmfwcxl/zbgs/jl/index.shtml",  #97
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'监理'}), f2],

    ["gcjs_buyi_jl_gg",
     "http://zjw.taiyuan.gov.cn/ggfw/bmfwcxl/bytz/jl/index.shtml",  #97
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'监理'}), f2],

    ["gcjs_kongzhijia_jl_gg",
     "http://zjw.taiyuan.gov.cn/ggfw/bmfwcxl/kzjgs/jl/index.shtml",  #97
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'监理'}), f2],

    ["gcjs_buyi_hw_gg",
     "http://zjw.taiyuan.gov.cn/ggfw/bmfwcxl/bytz/hw/index.shtml",  #97
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'货物'}), f2],

    ["gcjs_zhongbiao_hw_gg",
     "http://zjw.taiyuan.gov.cn/ggfw/bmfwcxl/zbgs/hw/index.shtml",  #97
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'货物'}), f2],

    ["gcjs_zhaobiao_kc_gg",
     "http://zjw.taiyuan.gov.cn/ggfw/bmfwcxl/zbgg/kc/index.shtml",  # 17
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'勘察'}), f2],

    ["gcjs_zhongbiao_kc_gg",
     "http://zjw.taiyuan.gov.cn/ggfw/bmfwcxl/zbgs/kc/index.shtml",  # 17
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'勘察'}), f2],

    ["gcjs_kongzhijia_kc_gg",
     "http://zjw.taiyuan.gov.cn/ggfw/bmfwcxl/kzjgs/kc/index.shtml",  # 17
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'勘察'}), f2],

    ["gcjs_buyi_kc_gg",
     "http://zjw.taiyuan.gov.cn/ggfw/bmfwcxl/bytz/kc/index.shtml",  # 17
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'勘察'}), f2],

    ["gcjs_zhaobiao_sj_gg",
     "http://zjw.taiyuan.gov.cn/ggfw/bmfwcxl/zbgg/sj/index.shtml",#48
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'设计'}), f2],

    ["gcjs_zhongbiao_sj_gg",
     "http://zjw.taiyuan.gov.cn/ggfw/bmfwcxl/zbgs/sj/index.shtml",#48
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'设计'}), f2],

    ["gcjs_kongzhijia_sj_gg",
     "http://zjw.taiyuan.gov.cn/ggfw/bmfwcxl/kzjgs/sj/index.shtml",#48
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'设计'}), f2],

    ["gcjs_buyi_sj_gg",
     "http://zjw.taiyuan.gov.cn/ggfw/bmfwcxl/bytz/sj/index.shtml",#48
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'设计'}), f2],

    ["gcjs_gqita_zhao_bian_qt_gg",
     "http://zjw.taiyuan.gov.cn/ggfw/bmfwcxl/zbgg/qt/index.shtml", #72
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'其他'}), f2],

    ["gcjs_buyi_qt_gg",
     "http://zjw.taiyuan.gov.cn/ggfw/bmfwcxl/bytz/qt/index.shtml", #72
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'其他'}), f2],

    ["gcjs_zhongbiao_qt_gg",
     "http://zjw.taiyuan.gov.cn/ggfw/bmfwcxl/zbgs/qt/index.shtml", #72
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'其他'}), f2],

    ["gcjs_kongzhijia_qt_gg",
     "http://zjw.taiyuan.gov.cn/ggfw/bmfwcxl/kzjgs/qt/index.shtml", #72
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'其他'}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="山西省太原市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "shanxi1_taiyuan"]
    work(conp,num=3)
    # driver = webdriver.Chrome()
    # driver.get("http://zjw.taiyuan.gov.cn/ggfw/bmfwcxl/zbgg/qt/index.shtml")
    # f1(driver,10)
    # f1(driver,100)
    # f1(driver,5)
    # f1(driver,30)
    # print(f2(driver))
    # print(f3(driver, 'http://zjw.taiyuan.gov.cn/doc/2018/06/25/511602.shtml'))