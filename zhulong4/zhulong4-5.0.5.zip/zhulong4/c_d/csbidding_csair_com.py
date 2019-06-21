import json
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

_name_ = 'csbidding_csair_com'


def f1(driver, num):
    locator = (By.XPATH, '//ul[@id="list1"]/li')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//ul[@id="list1"]/li[1]/a').get_attribute("href")[-15:]
    cnum_temp = driver.find_element_by_xpath('//div[@class="paging-nav"]/div').text
    cnum = re.findall(r'(\d+)\/',cnum_temp)[0]
    if int(cnum) != int(num):
        url = re.sub(r"pageNo=\d+","pageNo="+str(num),driver.current_url)
        driver.get(url)
        locator = (By.XPATH, '//ul[@id="list1"]/li[1]/a[not(contains(@href,"%s"))]' % val)
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@id="list1"]/li')
    for content in content_list:
        name = content.xpath("./a/@title")[0].strip()
        url = 'https://csbidding.csair.com'+content.xpath("./a/@href")[0].strip()
        try:
            status = content.xpath("./a/i/text()")[0].strip()
        except:status = 'None'
        ggstart_time = content.xpath("./a/em/text()")[0].strip()
        info = json.dumps({'status':status},ensure_ascii=False)
        temp = [name, ggstart_time, url,info]
        data.append(temp)
        # print('temp', temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="paging-nav"]/div')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_temp = driver.find_element_by_xpath('//div[@class="paging-nav"]/div').text
    total_page = re.findall(r'\/(\d+)',total_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="article-content"]')
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
    div = soup.find('div', class_='article-content')
    return div


data = [
    ["qy_zhaobiao_gg",
     "https://csbidding.csair.com/cms/channel/zbgg/index.htm?pageNo=1",
     ["name", "ggstart_time", "href","info"], f1, f2],
    ["qy_zhongbiaohx_gg",
     "https://csbidding.csair.com/cms/channel/pbgs/index.htm?pageNo=1",
     ["name", "ggstart_time", "href","info"], f1, f2],
    ["qy_zhongbiao_gg",
     "https://csbidding.csair.com/cms/channel/bidzbgg/index.htm?pageNo=1",
     ["name", "ggstart_time", "href","info"], f1, f2],
    ["qy_liubiao_gg",
     "https://csbidding.csair.com/cms/channel/qtgg/index.htm?pageNo=1",
     ["name", "ggstart_time", "href","info"], f1, f2],

    ["qy_zhaobiao_fzb_gg",
     "https://csbidding.csair.com/cms/channel/cggg/index.htm?pageNo=2",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"tag":"非招标"}), f2],
    ["qy_zhongbiao_fzb_gg",
     "https://csbidding.csair.com/cms/channel/cgjg/index.htm?pageNo=2",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"tag":"非招标"}), f2],
    ["qy_biangeng_jg_sb_gg",
     "https://csbidding.csair.com/cms/channel/fzbqtgg/index.htm?pageNo=2",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"tag":"非招标"}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="中国南方航空采购招标网", **args)
    est_html(conp, f=f3, **args)

def main():
    conp = ["postgres", "since2015", "192.168.3.171", "anbang_qiye", "csbidding_csair_com"]
    work(conp)
if __name__ == "__main__":
    main()