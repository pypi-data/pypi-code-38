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

_name_ ='shanxi1_xinzhou'


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='jump-item']")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    cnum_temp = driver.find_element_by_xpath("//div[@class='jump-item']").text
    cnum = re.findall("第(\d+)\/", cnum_temp)[0]
    locator = (By.XPATH, '//div[@class="aon-con"]/ul/li')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//div[@class="aon-con"]/ul/li[1]/a').get_attribute("href")[-20:]

    if int(cnum) != int(num):
        url = re.sub(r"[_]?[\d]*\.html",r"%s.html"%('_'+str(num-1) if str(num)!='1' else ''),driver.current_url)

        driver.get(url)
        locator = (By.XPATH, '//div[@class="aon-con"]/ul/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//div[@class="aon-con"]/ul/li')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="aon-con"]/ul/li')
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url_temp = content.xpath("./a/@href")[0].strip('.')
        if 'http' in url_temp:url = url_temp
        else:url = 'http://zjj.sxxz.gov.cn/zbgg'+content.xpath("./a/@href")[0].strip('.')
        temp = [name, ggstart_time, url]
        data.append(temp)

    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='jump-item']")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_temp = driver.find_element_by_xpath("//div[@class='jump-item']").text
    total_page = re.findall("\/(\d+)页", total_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    time.sleep(0.1)

    locator = (By.XPATH, "//div[@class='con1']|//table[@class='border2']")
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
     "http://zjj.sxxz.gov.cn/zbgg/index.html", #992
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="山西省忻州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "shanxi1_xinzhou"]
    work(conp,num=4,pageloadstrategy='none',headless=False)
    # driver = webdriver.Chrome()
    # driver.get("http://zjj.sxxz.gov.cn/zbgg/index.html")
    # f1(driver,1)
    # f1(driver,5)
    # f1(driver,2)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://zjj.sxxz.gov.cn/zbgg/201902/t20190227_2715616.html'))
    # driver.close()