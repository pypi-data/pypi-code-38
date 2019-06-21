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



from zhulong4.util.etl import est_tbs, est_meta, est_html, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url = "http://www.fqztb.com/Home/tenderList?index=3&type=%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE"
# driver = webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_ = 'thzb_crsc_cn'


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="second-lb-module-module"]/div[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('mp(\d+).aspx', url)[0]

    if num != int(cnum):
        val = driver.find_element_by_xpath('//div[@class="second-lb-module-module"]/div[1]//a').get_attribute('href')[
              -20:-5]
        url = re.sub('mp(\d+).aspx', 'mp%s.aspx' % num, url)
        driver.get(url)

        locator = (By.XPATH, '//div[@class="second-lb-module-module"]/div[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find_all('div', class_='second-lb-item')

    for tr in div:
        href = tr.find('a')['href']
        name = tr.find('a')['title']
        ggstart_time = tr.find('div', class_='second-lb-item-date').get_text().strip()

        if 'http' in href:
            href = href
        else:
            href = 'http://thzb.crsc.cn' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)

    df = pd.DataFrame(data=data)
    df['info'] = None

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="second-lb-module-module"]/div[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        total = driver.find_element_by_xpath('//a[@class="i-pager-last"]').get_attribute('page')
    except:
        driver.find_element_by_xpath('//div[@class="second-lb-module-module"][count(div[@class="second-lb-item"])>1]')
        total=1
    driver.quit()

    return int(total)



def f3(driver, url):

    driver.get(url)
    locator = (By.XPATH, '//div[@class="detail-content"][string-length()>10]')
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

    div = soup.find('div', class_="detail-content")


    return div


data = [
    ["qy_zhaobiao_gg", "http://thzb.crsc.cn/g2586/m5978/mp1.aspx",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_gqita_da_bian_gg", "http://thzb.crsc.cn/g2588/m5981/mp1.aspx",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_zhongbiaohx_gg", "http://thzb.crsc.cn/g2625/m6044/mp1.aspx",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_gqita_gg", "http://thzb.crsc.cn/g2668/m6090/mp1.aspx",["name", "ggstart_time", "href", "info"], f1, f2],

    ["qy_zhaobiao_tanpan_gg", "http://thzb.crsc.cn/g2670/m6093/mp1.aspx",["name", "ggstart_time", "href", "info"], add_info(f1,{"zbfs":"谈判"}), f2],
    ["qy_zhaobiao_xunjia_gg", "http://thzb.crsc.cn/g2671/m6094/mp1.aspx",["name", "ggstart_time", "href", "info"], add_info(f1,{"zbfs":"询价"}), f2],
    ["qy_zhongbiaohx_caigou_gg", "http://thzb.crsc.cn/g4374/m9194/mp1.aspx",["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"采购成交"}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="中国铁路通信信号集团", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch3", "thzb_crsc_cn"])
    pass