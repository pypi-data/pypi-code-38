import math
import time

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json



from zhulong4.util.etl import est_tbs, est_meta, est_html, add_info,est_meta_large

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url = "http://www.fqztb.com/Home/tenderList?index=3&type=%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE"
# driver = webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_ = 'www_bidding_csg_cn'


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="W750 Right"]//li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('index_(\d+).jhtml', url)[0]

    if num != int(cnum):
        val = driver.find_element_by_xpath('//div[@class="W750 Right"]//li[1]/a').get_attribute('href')[-20:-2]

        url = re.sub('index_\d+.jhtml', 'index_%s.jhtml' % num, url)
        driver.get(url)

        locator = (By.XPATH, '//div[@class="W750 Right"]//li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='W750 Right')
    trs = div.find_all('li')

    for tr in trs:
        ggstart_time = tr.span.extract().get_text()
        href = tr.a['href']
        name = tr.a.get_text().strip()
        tr.a.extract()
        company = tr.get_text()
        company = re.findall('\[(.*)\]', company)[0]

        if 'http' in href:
            href = href
        else:
            href = 'http://www.bidding.csg.cn' + href

        info = {'company': company}
        info = json.dumps(info, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]

        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="W750 Right"]//li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//div[@class="Top10 TxtCenter"]//a[last()]').get_attribute('href')
    total = re.findall('index_(\d+).jhtml', total)[0]

    driver.quit()

    return int(total)



def f3(driver, url):

    driver.get(url)
    locator = (By.XPATH, '//div[@class="Contnet"][string-length()>10]')
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    time.sleep(0.1)
    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 10: break

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    div = soup.find('div', class_="Contnet")


    return div


data = [
    ["qy_zhaobiao_gg", "http://www.bidding.csg.cn/zbgg/index_1.jhtml",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_zhaobiao_feigong_gg", "http://www.bidding.csg.cn/fzbgg/index_1.jhtml",["name", "ggstart_time", "href", "info"], add_info(f1,{"zbfs":'非公开'}), f2],
    ["qy_zhongbiaohx_gg", "http://www.bidding.csg.cn/zbhxrgs/index_1.jhtml",["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="中国南方电网有限责任公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch3", "www_bidding_csg_cn"])
    pass