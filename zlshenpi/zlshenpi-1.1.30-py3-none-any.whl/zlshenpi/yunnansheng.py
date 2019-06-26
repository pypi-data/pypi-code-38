import math
import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zlshenpi.util.etl import add_info, est_meta, est_html, est_tbs, add_info
import sys
import time
import json

_name_ = "yunnansheng"


def f1(driver, num):
    locator = (By.XPATH, "//table[@id='doingId']/tbody/tr[child::td][1]/td/a")
    val = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).get_attribute('href')
    locator = (By.XPATH, '//a[@class="numberstyle"]')
    cnum = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text

    if num != int(cnum):
        new_url = re.sub('CurPage=\d+', 'CurPage=' + str(num), driver.current_url)

        driver.get(new_url)

        locator = (By.XPATH, '//table[@id="doingId"]/tbody/tr[child::td][1]/td/a[not(contains(@href, "%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    contents = body.xpath("//table[@id='doingId']/tbody/tr[child::td]")
    for content in contents:
        name = content.xpath('./td/a/text()')[0].strip()
        ggstart_time = content.xpath('./td[last()]/text()')[0].strip()
        xm_code = content.xpath('./td[1]/text()')[0].strip('[').strip(']').strip()
        href = 'http://zxjg.yn.gov.cn' + content.xpath('./td/a/@href')[0].strip()

        info = json.dumps({'xm_code': xm_code}, ensure_ascii=False)

        tmp = [name, ggstart_time, href, info]
        # print(tmp)
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="page"]/li/a/span[1]')
    total_page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@id="projInfoId"]')
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
    div = soup.find('div', id='projInfoId')

    return div


data = [

    ["xm_shenpi_gg",
     "http://zxjg.yn.gov.cn/zxjg/kj?doingCurPage=1&id=0&daima=&quyu=&name=&test=&approve_type=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["xm_kaigong_gg",
     "http://zxjg.yn.gov.cn/zxjg/kj?doingCurPage=2&id=1&&daima=&quyu=&name=&test=&approve_type=",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["xm_jungong_gg",
     "http://zxjg.yn.gov.cn/zxjg/kj?doingCurPage=2&id=2&&daima=&quyu=&name=&test=&approve_type=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="云南省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlshenpi", "yunnansheng"],total=30, )
