import json
import math
import re

import requests
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong4.util.etl import est_html, est_meta, add_info
import time

_name_ = 'ec_ceec_net_cn'


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="real_news_show"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//div[@class="real_news_show"]/div[not(@id)][child::span/a]/span/a').get_attribute("href")[-50:]
    cnum = driver.find_element_by_xpath('//font[@color="red"]').text
    if int(cnum) != int(num):

        url = re.sub('PageD=\d+', 'PageD=' + str(num), driver.current_url)
        driver.get(url)
        locator = (By.XPATH, '''//div[@class="real_news_show"]/div[not(@id)][child::span/a]/span/a[not(contains(@href,"%s"))]''' % val)
        for _ in range(5):
            try:
                WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
                break
            except: driver.refresh()
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="real_news_show"]/div[not(@id)][child::span/a]')
    for content in content_list:
        name = content.xpath("./span/a/text()")[0].strip()
        url = "http://ec.ceec.net.cn/HomeInfo/" + content.xpath("./span/a/@href")[0].strip()
        if "QwBHAEcARwA" in driver.current_url:
            ggstart_time = content.xpath("./span[4]/text()")[0].strip()
            status = content.xpath("./span[3]/text()")[0].strip()
            info = json.dumps({'status':status},ensure_ascii=False)
        else:
            ggstart_time = content.xpath("./span[3]/text()")[0].strip()
            info = None
        temp = [name, ggstart_time, url,info]
        data.append(temp)

    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    # driver.maximize_window()
    locator = (By.XPATH, '//font[@color="green"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_temp = driver.find_element_by_xpath('//font[@color="green"]').text
    total_page = re.findall(r'共(\d+)页', total_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//*[@id="zwPanel"]|//table[@style="width:1100px;"]|//table[@align="center"]')
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
    div = soup.find('div', id='zwPanel')
    if div == None:
        div = soup.find('table', style="width:1100px;")
        if div == None:
            div = soup.find('table', align='center')
    return div


data = [
    ["qy_zhaobiao_gg",
     "http://ec.ceec.net.cn/HomeInfo/ProjectList.aspx?InfoLevel=MQA=&bigType=WgBCAEcARwA=&smallType=aAB3AA==&PageD=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_yucai_gg",
     "http://ec.ceec.net.cn/HomeInfo/ProjectList.aspx?InfoLevel=MQA=&bigType=QwBHAFkARwA=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qy_zhaobiao_caigou_hw_gg",
     "http://ec.ceec.net.cn/HomeInfo/ProjectList.aspx?InfoLevel=MgA=&bigType=QwBHAEcARwA=&smallType=aAB3AA==&PageD=1",
     ["name", "ggstart_time", "href","info"], add_info(f1,{'type':"货物"}), f2],
    ["qy_zhaobiao_caigou_gc_gg",
     "http://ec.ceec.net.cn/HomeInfo/ProjectList.aspx?InfoLevel=MgA=&bigType=QwBHAEcARwA=&smallType=ZwBjAA==&PageD=1",
     ["name", "ggstart_time", "href","info"], add_info(f1,{'type':"工程"}), f2],
    ["qy_zhaobiao_caigou_fw_gg",
     "http://ec.ceec.net.cn/HomeInfo/ProjectList.aspx?InfoLevel=MgA=&bigType=QwBHAEcARwA=&smallType=ZgB3AA==&PageD=1",
     ["name", "ggstart_time", "href","info"], add_info(f1,{'type':"服务"}), f2],

    ["qy_zhongbiao_hw_gg",
     "http://ec.ceec.net.cn/HomeInfo/ProjectList.aspx?InfoLevel=MgA=&bigType=WgBCAEcAUwA=&smallType=aAB3AA==&PageD=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'type':"货物"}), f2],
    ["qy_zhongbiao_gc_gg",
     "http://ec.ceec.net.cn/HomeInfo/ProjectList.aspx?InfoLevel=MgA=&bigType=WgBCAEcAUwA=&smallType=ZwBjAA==&PageD=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'type':"工程"}), f2],
    ["qy_zhongbiao_fw_gg",
     "http://ec.ceec.net.cn/HomeInfo/ProjectList.aspx?InfoLevel=MgA=&bigType=WgBCAEcAUwA=&smallType=ZgB3AA==&PageD=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'type':"服务"}), f2],

    ["qy_zhongbiaohx_hw_gg",
     "http://ec.ceec.net.cn/HomeInfo/ProjectList.aspx?InfoLevel=MgA=&bigType=WgBYAEcAUwA=&smallType=aAB3AA==&PageD=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'type':"货物"}), f2],
    ["qy_zhongbiao_gc_gg",
     "http://ec.ceec.net.cn/HomeInfo/ProjectList.aspx?InfoLevel=MgA=&bigType=WgBYAEcAUwA=&smallType=ZwBjAA==&PageD=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'type':"工程"}), f2],
    ["qy_zhongbiao_fw_gg",
     "http://ec.ceec.net.cn/HomeInfo/ProjectList.aspx?InfoLevel=MgA=&bigType=WgBYAEcAUwA=&smallType=ZgB3AA==&PageD=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'type':"服务"}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="中国能建电子采购平台", **args)
    est_html(conp, f=f3, **args)


def main():
    conp = ["postgres", "since2015", "192.168.3.171", "anbang_qiye", "ec_ceec_net_cn"]
    work(conp)

if __name__ == "__main__":
    main()
