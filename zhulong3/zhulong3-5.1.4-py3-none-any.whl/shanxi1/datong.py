import json
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

_name_ = 'shanxi1_datong'


def f1(driver, num):
    locator = (By.ID, "jumppage")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    cnum = int(driver.find_element_by_xpath("//input[@id='jumppage']").get_attribute('value'))
    locator = (By.XPATH, "//tbody[@id='contextid']/tr")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//tbody[@id='contextid']/tr[1]/td/a").get_attribute("href")[-20:]
    # print("cnum",cnum,"val",val)
    if int(cnum) != int(num):
        url = re.sub(r"cpage=\d+", 'cpage=' + str(num), driver.current_url)
        driver.get(url)
        locator = (By.XPATH, "//tbody[@id='contextid']/tr[1]/td/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//tbody[@id='contextid']/tr")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//tbody[@id='contextid']/tr")
    for content in content_list:
        name = content.xpath("./td[1]/a/text()")[0].strip()
        company = content.xpath("./td[2]/text()")[0].strip()
        ggstart_time, ggend_time = content.xpath("./td[3]/font/text()")[0].strip().split('~')
        url = 'http://www.dtjsgcjy.com' + content.xpath(".//td[1]/a/@href")[0].strip()
        info = json.dumps({'company': company, 'ggend_time': ggend_time})
        temp = [name, ggstart_time, url, info]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.ID, "allpages")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_page = driver.find_element_by_xpath('//span[@id="allpages"]').text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.ID, "menucontent1")
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
    div = soup.find('div', id='menucontent1')
    return div


data = [
    ["gcjs_zhaobiao_shiqu_gg",
     "http://www.dtjsgcjy.com/biddate/page2/zbgg2.jsp?notesType=1&cpage=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '市区'}), f2],
    ["gcjs_zhaobiao_xianqu_gg",
     "http://www.dtjsgcjy.com/biddate/page2/zbgg2.jsp?notesType=2&cpage=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '县区'}), f2],
    ["gcjs_zhaobiao_zhuanye_gg",
     "http://www.dtjsgcjy.com/biddate/page2/zbgg2.jsp?notesType=3&cpage=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '专业'}), f2],
    ["gcjs_zhongbiao_gg",
     "http://www.dtjsgcjy.com/biddate/page2/zbgs2.jsp?cpage=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="山西省大同市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "shanxi1_datong"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://www.dtjsgcjy.com/biddate/page2/zbgg2.jsp?notesType=1&cpage=1")
    # f1(driver,10)
    # f1(driver,100)
    # f1(driver,5)
    # f1(driver,30)
    #
    # print(f2(driver))

    # print(f3(driver, 'http://www.dtjsgcjy.com/biddate/page2/zbgg3.jsp?nid=16737'))
