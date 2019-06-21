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
from zhulong4.util.etl import est_html, est_meta, add_info
import time

_name_ = 'caigou_ceair_com'


def f1(driver, num):
    locator = (By.XPATH, '//table[@class="uk-table uk-table-striped vm-table-project uk-h6"]/tbody/tr')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//table[@class="uk-table uk-table-striped vm-table-project uk-h6"]/tbody/tr[1]/td[2]/a').get_attribute("href")[-20:]
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,'//li[@class="uk-active"]/span')))
    cnum = driver.find_element_by_xpath('//li[@class="uk-active"]/span').text
    if int(cnum) != int(num):
        url = re.sub('p=\d+','p='+str(num),driver.current_url)
        # print(url)
        driver.get(url)
        locator = (By.XPATH, '//table[@class="uk-table uk-table-striped vm-table-project uk-h6"]/tbody/tr[1]/td[2]/a[not(contains(@href,"%s"))]' % val)
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@class="uk-table uk-table-striped vm-table-project uk-h6"]/tbody/tr')
    for content in content_list:
        name = re.sub('\s+','',content.xpath('./td[2]/a/text()')[0].strip())
        url = "http://caigou.ceair.com" + content.xpath('./td[2]/a/@href')[0].strip()
        ggstart_time = '网站无时间。'
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print('temp', temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    driver.refresh()
    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="dataHtmlPages uk-pagination"]/li')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_page = driver.find_element_by_xpath('//ul[@class="dataHtmlPages uk-pagination"]/li[last()]').text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    time.sleep(0.1)
    locator = (By.XPATH, '//div[@class="uk-panel uk-panel-box"]')
    WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('div', class_='uk-panel uk-panel-box')
    return div


data = [
    ["qy_zhaobiao_caigou_gg",
     "http://caigou.ceair.com/com/Notice.aspx?cid=20&p=1",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"Tag":"采购"}), f2],
    ["qy_zhongbiao_caigou_gg",
     "http://caigou.ceair.com/com/Notice.aspx?cid=19&p=1",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"Tag":"采购"}), f2],

    ["qy_zhaobiao_gg",
     "http://caigou.ceair.com/com/Notice.aspx?cid=3&p=1",
     ["name", "ggstart_time", "href","info"], f1, f2],
    ["qy_biangeng_gg",
     "http://caigou.ceair.com/com/Notice.aspx?cid=4&p=1",
     ["name", "ggstart_time", "href","info"], f1, f2],
    ["qy_zhongbiaohx_gg",
     "http://caigou.ceair.com/com/Notice.aspx?cid=5&p=1",
     ["name", "ggstart_time", "href","info"], f1, f2],

    ["qy_zhongbiao_gg",
     "http://caigou.ceair.com/com/Notice.aspx?cid=6&p=1",
     ["name", "ggstart_time", "href","info"], f1, f2],
]



##要登录,无法爬取

def work(conp, **args):
    est_meta(conp, data=data, diqu="中国东方航空采购招标网", **args)
    est_html(conp, f=f3, **args)

def main():
    conp = ["postgres", "since2015", "192.168.3.171", "anbang_qiye", "caigou_ceair_com"]
    work(conp,pageloadtimeout=40,pageloadstrategy="none")
    # driver = webdriver.Chrome()
    # driver.get("http://caigou.ceair.com/com/Notice.aspx?cid=20&p=1")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 8)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # driver.get("http://caigou.ceair.com/com/Notice.aspx?cid=3&p=1")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 8)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://caigou.ceair.com/com/NoticeDetails.aspx?nid=2862'))
    # driver.close()
if __name__ == "__main__":
    main()