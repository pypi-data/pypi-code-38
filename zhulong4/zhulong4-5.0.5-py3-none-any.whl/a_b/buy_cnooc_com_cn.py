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
from zhulong4.util.etl import est_html, est_meta, add_info, est_meta_large
import time

_name_ = 'buy_cnooc_com_cn'


def f1(driver, num):
    # driver.set_window_size(1366,768)
    locator = (By.XPATH, '//div[@id="categorypagingcontent"]/ul/li')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//div[@id="categorypagingcontent"]/ul/li[1]/a').get_attribute("href")[-40:]
    cnum_temp = driver.find_element_by_xpath('//td[@class="huifont"][2]').text
    cnum = re.findall("(\d+)\/",cnum_temp)[0]
    # print(val,cnum)
    if int(cnum) != int(num):
        url = re.sub(r"(\d+)\.html",str(num)+'.html',driver.current_url)
        # print(url)
        driver.get(url)

        locator = (By.XPATH, '//div[@id="categorypagingcontent"]/ul/li[1]/a[not(contains(@href,"%s"))]' % val)
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@id="categorypagingcontent"]/ul/li')
    for content in content_list:
        name = content.xpath('./a/text()')[0].strip()
        url = "https://buy.cnooc.com.cn"+content.xpath('./a/@href')[0].strip()
        ggstart_time =  content.xpath("./span/text()")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print('temp', temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    # driver.execute_script("window.scrollBy(0,document.body.scrollHeight)", "")
    # driver.execute_script("javascript:getBidList('151','-1',1);")

    locator = (By.XPATH, '//td[@class="huifont"][2]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_temp = driver.find_element_by_xpath('//td[@class="huifont"][2]').text
    total_page = re.findall("\/(\d+)",total_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="now-bd"]')
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
    div = soup.find('div', class_='now-bd')
    return div


data = [
    ["qy_gqita_bian_zhao_gg",
     "https://buy.cnooc.com.cn/cbjyweb/001/001001/1.html",
     ["name", "ggstart_time", "href","info"], f1, f2],
    ["qy_zhongbiaohx_gg",
     "https://buy.cnooc.com.cn/cbjyweb/001/001002/1.html",
     ["name", "ggstart_time", "href","info"], f1, f2],
    ["qy_zhongbiao_gg",
     "https://buy.cnooc.com.cn/cbjyweb/001/001003/1.html",
     ["name", "ggstart_time", "href","info"], f1, f2],
    ["qy_zhaobiao_fzb_gg",
     "https://buy.cnooc.com.cn/cbjyweb/001/001003/1.html",
     ["name", "ggstart_time", "href","info"], add_info(f1,{'Tag':'非招标'}), f2],
]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="中国海洋石油集团有限公司", **args)
    est_html(conp, f=f3, **args)

def main():
    conp = ["postgres", "since2015", "192.168.3.171", "anbang_qiye", "buy_cnooc_com_cn"]
    work(conp,pageloadstrategy='none',pageloadtimeout=40)
    # driver = webdriver.Chrome()
    # driver.get("https://buy.cnooc.com.cn/cbjyweb/001/001001/1.html")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 8)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'https://buy.cnooc.com.cn/cbjyweb/001/001003/20190313/96f2613a-1b08-404e-a27c-4bc41f13ecc6.html'))
    # driver.close()
if __name__ == "__main__":
    main()