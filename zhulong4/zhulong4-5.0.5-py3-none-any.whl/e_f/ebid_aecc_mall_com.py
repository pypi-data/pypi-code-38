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
from zhulong4.util.etl import est_html, est_meta
import time

_name_ = 'ebid_aecc_mall_com'


def f1(driver, num):
    # driver.set_window_size(1366,768)
    locator = (By.XPATH, '//ul[@id="listId"]/li')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//ul[@id="listId"]/li[1]/div/h2/a').get_attribute("href")[-20:]
    cnum_temp = driver.find_element_by_xpath('//div[@id="pageId"]/span/em').text
    cnum = re.findall("(\d+)\/",cnum_temp)[0]
    # print(val,cnum)
    if int(cnum) != int(num):
        driver.execute_script("javascript:getBidList('151','-1',%s);"%num)
        locator = (By.XPATH, '//ul[@id="listId"]/li[1]/div/h2/a[not(contains(@href,"%s"))]' % val)
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@id="listId"]/li')
    for content in content_list:
        name = content.xpath('./div/h2/a/text()')[0].strip()
        url = "http://ebid.aecc-mall.com"+content.xpath('./div/h2/a/@href')[0].strip("..").strip()
        try:
            status = content.xpath("./div[2]/text()")[0].strip()
        except:status = "None"
        
        ggstart_time =  content.xpath("./div/span/text()")[0].strip()
        info = json.dumps({'status':status},ensure_ascii=False)
        temp = [name, ggstart_time, url,info]
        data.append(temp)
        # print('temp', temp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):


    locator = (By.XPATH, '//div[@id="pageId"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_temp = driver.find_element_by_xpath('//div[@id="pageId"]/span/em').text
    total_page = re.findall("\/(\d+)",total_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="edit_con_original"]')
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
    div = soup.find('div', class_='edit_con_original')
    return div


data = [
    ["qy_zhaobiao_gg",
     "http://ebid.aecc-mall.com/bid/index.html",
     ["name", "ggstart_time", "href","info"], f1, f2],
    ["qy_biangeng_gg",
     "http://ebid.aecc-mall.com/bid/change.html",
     ["name", "ggstart_time", "href","info"], f1, f2],
    ["qy_zhongbiaohx_gg",
     "http://ebid.aecc-mall.com/bid/winner.html",
     ["name", "ggstart_time", "href","info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="中国航空发动机集团", **args)
    est_html(conp, f=f3, **args)

def main():
    conp = ["postgres", "since2015", "192.168.3.171", "anbang_qiye", "ebid_aecc_mall_com"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://ebid.aecc-mall.com/bid/index.html")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 8)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://ebid.aecc-mall.com/content/details_151_16619.html'))
    # driver.close()
if __name__ == "__main__":
    main()