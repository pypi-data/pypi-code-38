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

_name_ = 'jilin_jilin'


def f1(driver, num):
    locator = (By.XPATH, '//a[@style="color:red"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath('//a[@style="color:red"]').text

    locator = (By.XPATH, '//div[@class="right"]/ul')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//div[@class="right"]/ul[1]/li/a').get_attribute('href')[-20:]
    num -=1
    if int(cnum) != int(num):
        url = re.sub(r"index[_\d]{0,5}\.html","%s%s.html"%('index_' if str(num)!='0' else 'index',str(num) if str(num)!='0' else ''),driver.current_url)
        driver.get(url)
        locator = (By.XPATH, '//div[@class="right"]/ul[1]/li/a[not(contains(@href,"%s"))]' % val)
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="right"]/ul')
    for content in content_list:
        name = content.xpath("./li/a/text()")[0].strip()
        url = 'http://jw.jlcity.gov.cn/zbzb/%s'%("zbxx" if "zbxx" in driver.current_url else "zbgg")+content.xpath("./li/a/@href")[0].strip('.')
        ggstart_time = content.xpath("./li/span/text()")[0].strip('[').strip(']')
        temp = [name, ggstart_time,url]
        data.append(temp)
        # print('temp',temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@id="fenye"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_page = driver.find_element_by_xpath('//div[@id="fenye"]/dl/dd[last()-2]/a | //div[@id="fenye"]/dl/dd[last()-2]/a/span').text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='right']")
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
    div = soup.find('div', class_='right')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://jw.jlcity.gov.cn/zbzb/zbgg/index.html",
     ["name", "ggstart_time", "href","info"],f1,f2],
    ["gcjs_zhongbiao_gg",
     "http://jw.jlcity.gov.cn/zbzb/zbxx/index.html",
     ["name", "ggstart_time", "href","info"],f1,f2],

]

def work(conp, **args):
    est_meta(conp, data=data, diqu="吉林省吉林市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "jilin_jilin"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://jw.jlcity.gov.cn/zbzb/zbxx/index.html")
    # f1(driver,30)
    # f1(driver,100)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://jw.jlcity.gov.cn/zbzb/zbgg/201901/t20190118_537905.html'))
    # driver.close()
