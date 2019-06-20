import json

import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write, db_command, db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

from zhulong2.util.etl import est_meta, est_html, add_info

_name_ = 'shanxi1_changzhi'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="print-area1"]')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
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
    div = soup.find('div', class_='print-area1')
    return div


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='pages-govinfo-open group']")
    txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall('(\d+)\/\d+页',txt)[0]
    # print('val', val, 'cnum', cnum)
    locator = (By.XPATH, "//ul[@class='govinfo-list-title']/li[1]/a")
    val = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).get_attribute('href')[-30:]
    if int(cnum) != int(num):
        new_url = re.sub('index[_\d]*', 'index_' + str(num-1) if num != 1 else 'index', driver.current_url)

        driver.get(new_url)

        locator = (By.XPATH, '//ul[@class="govinfo-list-title"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//ul[@class='govinfo-list-title']/li")
    for content in content_list:
        name = content.xpath("./a/@title")[0].strip()
        # print(name)
        ggstart_time = content.xpath("./span[last()]/text()")[0].strip()
        fawenzihao =  content.xpath("./span[2]/@title")[0].strip()
        url = "http://www.changzhi.gov.cn/"+content.xpath("./a/@href")[0].split('..')[-1]
        try:
            info = json.dumps({'发文字号':fawenzihao},ensure_ascii=False)
        except:
            info = 'none'
        temp = [name, ggstart_time, url,info]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='pages-govinfo-open group']")
    txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text
    total_page = re.findall('\/(\d+)页',txt)[0]
    # print('total_page', total_page)
    driver.quit()
    return int(total_page)


data = [
    #
    ["zfcg_zhaobiao_gg","http://www.changzhi.gov.cn/zwgk/zdxxgkzl1/czzj_7215/zfcg_7223/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="陕西省长治市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "shanxi1_changzhi"])
    # driver = webdriver.Chrome()
    # driver.get('http://www.changzhi.gov.cn/zwgk/zdxxgkzl1/czzj_7215/zfcg_7223/index.shtml')
    # f1(driver,107)