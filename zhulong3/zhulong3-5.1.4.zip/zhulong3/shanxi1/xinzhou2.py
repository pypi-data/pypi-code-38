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

_name_ ='shanxi1_xinzhou2'

total_page = 552

def f1(driver, num):
    locator = (By.XPATH, '//td[1][@height="300"]/table[1]/tbody/tr/td/a')
    val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')[-40:]

    locator = (By.XPATH, "//font[@color='red']")
    cnum = int(WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text.strip('[').strip(']'))

    if int(cnum) != int(num):
        new_url = re.sub(r"index_\d+","index_" + str(total_page-num+1),driver.current_url)

        driver.get(new_url)
        locator = (By.XPATH, '//td[1][@height="300"]/table[1]/tbody/tr/td/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//td[1][@height="300"]/table')
    for content in content_list:
        name = content.xpath("./tbody/tr/td/a/@title")[0].strip()
        ggstart_time = content.xpath("./tbody/tr/td[2]/font/text()")[0].strip()
        url= content.xpath("./tbody/tr/td/a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)

    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    global total_page
    locator = (By.XPATH, "//a[@title='first page']")
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')

    total_page = int(re.findall("index_(\d+)", txt)[0])

    driver.quit()
    return total_page


def f3(driver, url):
    driver.get(url)
    time.sleep(0.1)

    locator = (By.XPATH, "//table[@class='border2']")
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
    div = soup.find('div', class_='con1')
    if not div:div = soup.find('table', class_='border2')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.xzgcjy.com/pull/index_552_5.html", #992
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://www.xzgcjy.com/result/index_265_6.html", #992
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="山西省忻州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "shanxi1_xinzhou2"]
    work(conp,num=4)
    # driver = webdriver.Chrome()
    # driver.get("http://www.xzgcjy.com/pull/index_552_5.html")
    # print(f2(driver))
    # f1(driver,3)
    # f1(driver,5)
    # f1(driver,2)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://zjj.sxxz.gov.cn/zbgg/201902/t20190227_2715616.html'))
    # driver.close()