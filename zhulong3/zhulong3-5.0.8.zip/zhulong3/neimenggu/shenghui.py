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
from zhulong3.util.etl import est_html, est_meta
import time

_name_ = 'neimenggu_shenghui'


def f1(driver, num):
    if 'kaibiaojilu' not in driver.current_url:
        locator = (By.XPATH, "//div[@class='epages']")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        cnum_temp = driver.find_element_by_xpath("//div[@class='epages']").text
        cnum = re.findall("(\d+)\/", cnum_temp)[0]
    else:
        cnum = 1
    locator = (By.XPATH, '//ul[@id="liebiao"]')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//ul[@id="liebiao"]/li[1]/a').get_attribute("href")[-40:]
    if int(cnum) != int(num):
        url = re.sub(r"page=\d+","page=%s"%(str(num)),driver.current_url)
        driver.get(url)
        locator = (By.XPATH, '//ul[@id="liebiao"]/li[1]/a[not(contains(@href,"%s"))]' % val)

        for _ in range(5):
            try:
                WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
                break
            except:
                driver.refresh()

    locator = (By.XPATH, '//ul[@id="liebiao"]/li')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@id="liebiao"]/li')
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip('[').strip(']')
        url = 'http://www.nmggcztb.cn'+content.xpath("./a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    if 'kaibiaojilu' not in driver.current_url:
        locator = (By.XPATH, "//div[@class='epages']")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        total_temp = driver.find_element_by_xpath("//div[@class='epages']").text
        total_page = re.findall("\/(\d+)", total_temp)[0]
    else:
        total_page = 1
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='left1']")
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
    div = soup.find('div', id='left1')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.nmggcztb.cn/html/gongcheng/zhaobiaogonggao/index.html?page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://www.nmggcztb.cn/html/gongcheng/zhongbiaogongshi/index.html?page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://www.nmggcztb.cn/html/gongcheng/zhongbiaojieguo/index.html?page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_kaibiao_gg",
     "http://www.nmggcztb.cn/html/gongcheng/kaibiaojilu/index.html?page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="内蒙古", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "neimenggu"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://www.nmggcztb.cn/html/gongcheng/zhaobiaogonggao/index.html?page=1")
    # f1(driver,10)
    # f1(driver,5)
    # f1(driver,31)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://www.nmggcztb.cn/gcxx/main.php?N=Notice&id=8bef5ac4-c743-4a56-a1bb-db9a50f61e88&d=o'))
    # driver.close()