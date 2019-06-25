import math
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

_name_ = 'zhejiang_jinhua'


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='Right-Border floatL']/dl/dt/a")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')

    locator = (By.XPATH, "//div[@class='Page-bg floatL']")
    cnum = re.findall(r'(\d+)\/', WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text)[0]

    if int(cnum) != int(num):
        url = re.sub('index[_\d]*', "index_" + str(num), driver.current_url)
        driver.get(url)
        locator = (By.XPATH, '//div[@class="Right-Border floatL"]/dl/dt/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@class='Right-Border floatL']/dl/dt")
    for content in content_list:
        name = content.xpath("./a/@title")[0].strip()
        url = 'http://www.jhztb.gov.cn' + content.xpath("./a/@href")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip().strip(']').strip('[')
        temp = [name, ggstart_time, url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='Page-bg floatL']")

    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text

    total_page = re.findall("\/(\d+)", txt)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="content-Border floatL"]')
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
    div = soup.find('div', class_='content-Border floatL')
    return div


data = [
    ["gcjs_gqita_zhao_bian_zhong_sheng_gg",
     "http://www.jhztb.gov.cn/jhztb/jsgcszdxm/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"省重点工程"}), f2],

    ["gcjs_gqita_zhao_bu_zhong_shi_gg",
     "http://www.jhztb.gov.cn/jhztb/jsgcgcjs/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"市本级工程"}), f2],

    ["gcjs_gqita_zhao_bu_zhong_jinhuashan_gg",
     "http://www.jhztb.gov.cn/jhztb/jsgcsjhslygc/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"金华山工程"}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="浙江省金华市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "zhejiang_jinhua"]
    work(conp,num=2)
    # driver = webdriver.Chrome()
    # driver.get("http://www.jhztb.gov.cn/jhztb/jsgcszdxm/index.htm")
    # f1(driver, 2)
    # f1(driver, 3)
    # print(f2(driver))
    # f1(driver, 10)
    # print(f2(driver))
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://www.zsptztb.com.cn//zsptztb/InfoDetail/?InfoID=c657cb46-5a8a-4d0f-beb9-9d9c367d8c18zbgg&CategoryNum=010008'))
    # driver.close()
