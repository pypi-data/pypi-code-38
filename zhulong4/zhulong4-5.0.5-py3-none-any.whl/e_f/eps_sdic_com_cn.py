import math
import re

import requests
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong4.util.etl import est_html, est_meta, add_info
import time

_name_ = 'eps_sdic_com_cn'


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="lb-link"]/ul/li')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//div[@class="lb-link"]/ul/li[1]/a').get_attribute("href")[-40:]
    cnum = driver.find_element_by_xpath('//div[@class="pag-txt"]/em[1]').text
    # print(val,cnum)
    if int(cnum) != int(num):
        url = re.sub(r"[_\d]*\.jhtml",('' if num == 1 else '_%s'%str(num) ) +'.jhtml',driver.current_url)
        # print(url)
        driver.get(url)
        locator = (By.XPATH, '//div[@class="lb-link"]/ul/li[1]/a[not(contains(@href,"%s"))]' % val)
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="lb-link"]/ul/li')
    for content in content_list:
        name = content.xpath('./a/@title')[0].strip()
        url = content.xpath('./a/@href')[0].strip()
        ggstart_time =  content.xpath("./a/span[last()]/text()")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print('temp', temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="pag-txt"]/em[2]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_page = driver.find_element_by_xpath('//div[@class="pag-txt"]/em[2]').text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="mbox lpInfo"]/div[@class="m-bd"]')
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
    div = soup.find('div', class_='mbox lpInfo')
    return div


data = [
    ["qy_zhaobiao_hw_gg",
     "http://eps.sdic.com.cn/gghw/index.jhtml",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"tag":"货物"}), f2],
    ["qy_zhaobiao_gc_gg",
     "http://eps.sdic.com.cn/gggc/index.jhtml",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"tag":"工程"}), f2],
    ["qy_zhaobiao_fw_gg",
     "http://eps.sdic.com.cn/ggjg/index.jhtml",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"tag":"服务"}), f2],


    ["qy_biangeng_hw_gg",
     "http://eps.sdic.com.cn/bghw/index.jhtml",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"tag":"货物"}), f2],
    ["qy_biangeng_gc_gg",
     "http://eps.sdic.com.cn/bggc/index.jhtml",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"tag":"工程"}), f2],
    ["qy_biangeng_fw_gg",
     "http://eps.sdic.com.cn/bgfw/index.jhtml",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"tag":"服务"}), f2],


    ["qy_zhongbiaohx_hw_gg",
     "http://eps.sdic.com.cn/zbhw/index.jhtml",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"tag":"货物"}), f2],
    ["qy_zhongbiaohx_gc_gg",
     "http://eps.sdic.com.cn/zbgc/index.jhtml",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"tag":"工程"}), f2],
    ["qy_zhongbiaohx_fw_gg",
     "http://eps.sdic.com.cn/zbfw/index.jhtml",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"tag":"服务"}), f2],


    ["qy_zhaobiao_caigou_hw_gg",
     "http://eps.sdic.com.cn/cghw/index.jhtml",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"tag":"货物"}), f2],
    ["qy_zhaobiao_caigou_gc_gg",
     "http://eps.sdic.com.cn/cggc/index.jhtml",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"tag":"工程"}), f2],
    ["qy_zhaobiao_caigou_fw_gg",
     "http://eps.sdic.com.cn/cgfw/index.jhtml",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"tag":"服务"}), f2],


    ["qy_zhongbiao_caigou_hw_gg",
     "http://eps.sdic.com.cn/kzjhw/index.jhtml",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"tag":"货物"}), f2],
    ["qy_zhongbiao_caigou_gc_gg",
     "http://eps.sdic.com.cn/kzjgc/index.jhtml",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"tag":"工程"}), f2],
    ["qy_zhongbiao_caigou_fw_gg",
     "http://eps.sdic.com.cn/kzjfw/index.jhtml",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"tag":"服务"}), f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="国家开发投资公司（国投集团）电子采购平台", **args)
    est_html(conp, f=f3, **args)

def main():
    conp = ["postgres", "since2015", "192.168.3.171", "anbang_qiye", "eps_sdic_com_cn"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://eps.sdic.com.cn/gggc/index_5.jhtml")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 8)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'https://buy.cnooc.com.cn/cbjyweb/001/001003/20190313/96f2613a-1b08-404e-a27c-4bc41f13ecc6.html'))
    # driver.close()
if __name__ == "__main__":
    main()