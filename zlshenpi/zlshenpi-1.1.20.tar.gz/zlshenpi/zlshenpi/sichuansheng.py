import os

import pandas as pd
import re

import requests
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from zlshenpi.util.fake_useragent import UserAgent

from zlshenpi.util.etl import add_info, est_meta, est_html, est_tbs, add_info, est_meta_large
import sys
import time
import json



_name_ = "sichuansheng"



def f1(driver, num):
    locator = (By.XPATH, '//table[@class="table_style"]/tbody/tr[1]/td/a')
    val = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).get_attribute('href')[-30:]

    # print(val)
    locator = (By.XPATH, "//a[@class='current-page']")
    cnum = int(WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text)
    if num != int(cnum):
        js = """goPage('%s')"""%(num)
        driver.execute_script(js)
        locator = (By.XPATH, """//table[@class="table_style"]/tbody/tr[1]/td/a[not(contains(@href, "%s"))]""" % val)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    body = etree.HTML(page)
    contents = body.xpath('//table[@class="table_style"]/tbody/tr')

    data = []
    for content in contents:
        xm_code = content.xpath("./td/a/text()")[0].strip().strip('【').strip('】')
        name = content.xpath("./td[2]/text()")[0].strip()
        href ='http://sc.tzxm.gov.cn' + content.xpath('./td/a/@href')[0].strip()
        shixiang = content.xpath('./td[3]/text()')[0].strip()
        bumen = content.xpath('./td[4]/text()')[0].strip()
        result = content.xpath('./td[5]/text()')[0].strip()
        try:
            ggstart_time = content.xpath('./td[6]/text()')[0].strip()
        except:ggstart_time = "None"
        info_tmp = {"shixiang": shixiang, 'bumen': bumen, "xm_code": xm_code,"result":result}
        if not href:
            info_tmp.update({'hreftype' : '不可抓网页'})
        info = json.dumps(info_tmp, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
        # print(tmp)
    df = pd.DataFrame(data)
    return df



def f2(driver):
    locator = (By.XPATH, '//*[@id="dvRight1"]/div/div/ul/li[5]/a')
    total_page = int(WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text)
    driver.quit()
    return total_page



def f3(driver, url):

    driver.get(url)
    locator = (By.XPATH, '//div[@class="t4_xm_table t4_bszn2_table"]')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('div', class_="t4_xm_table t4_bszn2_table")

    return div


data = [
    ["xm_jieguo_gg",
     "http://sc.tzxm.gov.cn/showinformation",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="四川省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlshenpi", "sichuansheng"])
    # op.add_argument("--headless")
    # driver = webdriver.Chrome()
    # driver.get("http://sc.tzxm.gov.cn/showinformation")
    # for i in range(1,20):
    # f1(driver, 33)

    # print(f2(driver))
    # print(f3(driver, """queryRecordContent('b2c52c399b9341faa0b0035c3251d3f8','0');"""))
