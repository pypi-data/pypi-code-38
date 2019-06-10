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

_name_ = 'shanxi1_linfen'


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="page"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    cnum_temp = driver.find_element_by_xpath('//div[@class="page"]/p').text
    cnum = re.findall("(\d+) \/", cnum_temp)[0]
    locator = (By.XPATH, '//div[@class="con"]/ul|//div[@class="con"]//ul')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//div[@class="con"]/ul[1]/li/a|//div[@class="con"]//ul[1]/li/a').get_attribute("href")[-20:]
    if int(cnum) != int(num):
        url = re.sub(r"(\d*)([_]?[\d]*)\.html", r"\1%s.html" % ( '_'+str(num) if str(num) != '1' else ''),driver.current_url)

        driver.get(url)
        locator = (By.XPATH, '//div[@class="con"]/ul[1]/li[1]/a[not(contains(@href,"%s"))]|//div[@class="con"]//ul[1]/li[1]/a[not(contains(@href,"%s"))]' % (val,val))
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, '//div[@class="con"]/ul|//div[@class="con"]//ul')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="con"]/ul|//div[@class="con"]//ul')
    for content in content_list:
        name = content.xpath("./li[1]/a/text()")[0].strip()
        ggstart_time = content.xpath("./li[3]/text()")[0].strip()
        url = 'http://www.linfen.gov.cn'+content.xpath("./li[1]/a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="page"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_temp = driver.find_element_by_xpath('//div[@class="page"]/p').text
    total_page = re.findall("\/ (\d+)", total_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='cont w']")
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
    div = soup.find('div', class_='cont w')
    return div


data = [
    ["gcjs_gqita_zhao_bian_kong_gg",
     "http://www.linfen.gov.cn/zhujian/channels/11353.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://www.linfen.gov.cn/zhujian/channels/11354.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="山西省临汾市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "shanxi1_linfen"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://www.linfen.gov.cn/zhujian/channels/11353_2.html")
    # f1(driver,10)
    # f1(driver,1)
    # f1(driver,23)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://www.linfen.gov.cn/zhujian/contents/11353/548801.html'))
    # driver.close()