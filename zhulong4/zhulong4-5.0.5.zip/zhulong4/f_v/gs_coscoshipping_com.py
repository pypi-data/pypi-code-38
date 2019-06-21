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


_name_ = 'gs_coscoshipping_com'


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="w1000 cg2"]//li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('page=(\d+?)&', url)[0]


    if int(cnum)+1 != num:
        val = driver.find_element_by_xpath('//div[@class="w1000 cg2"]//li[1]/a').get_attribute('href')[-20:]

        url = re.sub('page=(\d+?)&', 'page=%s&'%(num-1), url)
        driver.get(url)
        locator = (By.XPATH, '//div[@class="w1000 cg2"]//li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='w1000 cg2')
    trs = div.find_all('li')
    for tr in trs:
        href = tr.a['href']
        name = tr.a.get_text()
        ggstart_time = tr.span.get_text()
        if 'http' in href:
            href = href
        else:
            href = 'http://gs.coscoshipping.com' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)

    df = pd.DataFrame(data=data)
    df["info"] = None

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="w1000 cg2"]//li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//div[@class="w1000 cg3"]/a[last()]').get_attribute('href')
    total = re.findall('page=(\d+?)&', total)[0]
    total=int(total)+1

    driver.quit()

    return total



def f3(driver, url):

    driver.get(url)
    locator = (By.XPATH, '//div[@class="cgnrbox "][string-length()>10]')
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

    div = soup.find('div', class_=re.compile('cgnrbox'))
    divs=div.find_all('div',class_="cgnrbox2 clear")
    for d in divs:
        d.extract()

    if div==None:
        raise ValueError('div is None')

    return div


data = [
    ["qy_yucai_feigong_gg", "http://gs.coscoshipping.com/e/action/ListInfo/index.php?page=0&classid=4",["name", "ggstart_time", "href", "info"], add_info(f1,{"zbfs":"非公招标"}), f2],
    ["qy_zhaobiao_gg", "http://gs.coscoshipping.com/e/action/ListInfo/index.php?page=1&classid=2",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_zhongbiao_gg", "http://gs.coscoshipping.com/e/action/ListInfo/index.php?page=1&classid=3",["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="中国远洋海运集团", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch3", "gs_coscoshipping_com"],num=1,headless=False)
    # pass
    # url = "http://gs.coscoshipping.com/e/action/ShowInfo.php?classid=3&id=1603"
    # # driver = webdriver.Chrome()
    # chrome_option=webdriver.ChromeOptions()
    # chrome_option.add_argument("--headless")
    # chrome_option.add_argument("--no-sandbox")
    # driver=webdriver.Chrome(chrome_options=chrome_option)
    # driver.minimize_window()
    # f3(driver,url)