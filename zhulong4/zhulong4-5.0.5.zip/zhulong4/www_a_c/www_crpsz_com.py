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


_name_ = 'www_crpsz_com'


def f1(driver, num):
    locator = (By.XPATH, '//tbody[@id="infocontent"]/tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('pageIndex=(\d+)', url)[0]

    if int(cnum) != num:
        val = driver.find_element_by_xpath('//tbody[@id="infocontent"]/tr[1]//a').get_attribute('href')[-30:-5]

        url = url.rsplit('=', maxsplit=1)[0] + '=%s' % num

        driver.get(url)

        locator = (By.XPATH, '//tbody[@id="infocontent"]/tr[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        locator=(By.XPATH,'//tbody[@id="infocontent"]/tr[1]/td[last()-1][string-length()=0]')
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('tbody', id='infocontent')
    trs = div.find_all('tr')
    for tr in trs:
        tds = tr.find_all('td')
        href = tds[1].a['href']
        name = tds[1].a['title']
        ggstart_time = tds[-1].get_text()
        zblx=tds[-2].get_text().strip()

        if 'http' in href:
            href = href
        else:
            href = 'https://szecp.crc.com.cn' + href
        info={'zblx':zblx}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time, href,info]

        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//tbody[@id="infocontent"]/tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        total = driver.find_element_by_xpath('//div[@id="page"]//li[last()]/a').get_attribute('title')
    except:

        total=1

    driver.quit()

    return int(total)



def f3(driver, url):

    driver.get(url)
    locator = (By.XPATH, '//div[@class="ewb-con-bd"][string-length()>10]')
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

    div = soup.find('div', class_="ewb-con-bd")


    return div


data = [
    ["qy_zhaobiao_gg", "https://szecp.crc.com.cn/zbxx/006001/006001001/secondpagejy.html?categoryNum=006001001&pageIndex=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_biangeng_gg", "https://szecp.crc.com.cn/zbxx/006001/006001002/secondpagejy.html?categoryNum=006001002&pageIndex=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_zhongbiaohx_gg", "https://szecp.crc.com.cn/zbxx/006001/006001003/secondpagejyNoStatuw.html?categoryNum=006001003&pageIndex=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_zhongbiao_gg", "https://szecp.crc.com.cn/zbxx/006001/006001004/secondpagejyNoStatuw.html?categoryNum=006001004&pageIndex=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_zhongzhi_gg", "https://szecp.crc.com.cn/zbxx/006001/006001005/secondpagejyNoStatuw.html?categoryNum=006001005&pageIndex=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_zhaobiao_feigong_gg", "https://szecp.crc.com.cn/zbxx/006002/006002001/secondpagejy.html?categoryNum=006002001&pageIndex=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'非公开招标'}), f2],
    ["qy_biangeng_feigong_gg", "https://szecp.crc.com.cn/zbxx/006002/006002002/secondpagejy.html?categoryNum=006002002&pageIndex=1",["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'非公开招标'}), f2],
]


#网址变更,https://szecp.crc.com.cn
#修改时间:2019-5-27



def work(conp, **args):
    est_meta(conp, data=data, diqu="华润集团", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch3", "www_crpsz_com"])
    pass