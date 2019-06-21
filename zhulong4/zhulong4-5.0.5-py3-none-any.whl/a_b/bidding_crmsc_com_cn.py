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

_name_ = 'bidding_crmsc_com_cn'


def f1(driver, num):
    driver.set_window_size(1366,768)
    locator = (By.XPATH, '//ul[@class="zblb"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//ul[@class="zblb"]/li[1]/div[@class="lfnr"]/div/a').get_attribute("href")[-15:]
    cnum = driver.find_element_by_xpath('//span[@id="pageNum"]').text
    locator = (By.XPATH, '//ul[@class="zblb"]/li')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    if int(cnum) != int(num):
        # driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
        driver.execute_script("page(%s)"%num)
        locator = (By.XPATH, '//ul[@class="zblb"]/li[1]/div[@class="lfnr"]/div/a[not(contains(@href,"%s"))]' % val)
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@class="zblb"]/li')
    for content in content_list:
        name = content.xpath("./div[@class='lfnr']/div[@class='shang']/a/text()")[0].strip()
        url = 'http://bidding.crmsc.com.cn'+content.xpath("./div[@class='lfnr']/div[@class='shang']/a/@href")[0].strip()
        zhaobiao_number = content.xpath(".//div[@class='xia']/div[1]/text()")[0].strip()
        zhaobiao_method = content.xpath(".//div[@class='xia']/div[2]/text()")[0].strip()
        try:
            biaoshu_sale_time = content.xpath(".//div[@class='xia']/div[3]/text()")[0].strip()
        except:biaoshu_sale_time = "None"
        
        ggstart_time = content.xpath("./div/div/div[@class='xia']/text()")[0].strip()+'-'+content.xpath("./div/div/div[@class='shang']/text()")[0].strip()

        info = json.dumps({'zhaobiao_number':zhaobiao_number,'zhaobiao_method':zhaobiao_method,'biaoshu_sale_time':biaoshu_sale_time},ensure_ascii=False)
        temp = [name, ggstart_time, url,info]
        data.append(temp)

    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, '//span[@id="pageTotal"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_page = driver.find_element_by_xpath('//span[@id="pageTotal"]').text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="lbej"]')
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
    div = soup.find('div', class_='lbej')
    return div


data = [
    ["qy_zhaobiao_gg",
     "http://bidding.crmsc.com.cn/bulletin",
     ["name", "ggstart_time", "href","info"], f1, f2],
    ["qy_zhongbiaohx_gg",
     "http://bidding.crmsc.com.cn/bid",
     ["name", "ggstart_time", "href","info"], f1, f2],
    ["qy_zhongbiao_gg",
     "http://bidding.crmsc.com.cn/bidBulletin",
     ["name", "ggstart_time", "href","info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="中铁物总国际招标有限公司", **args)
    est_html(conp, f=f3, **args)

def main():
    conp = ["postgres", "since2015", "192.168.3.171", "anbang_qiye", "bidding_crmsc_com_cn"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://bidding.crmsc.com.cn/bid")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 10)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://bidding.crmsc.com.cn/bulletin/look/15947'))
    # driver.close()
if __name__ == "__main__":
    main()