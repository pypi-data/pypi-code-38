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


_name_ = 'fwgs_sinograin_com_cn'


def f1(driver, num):
    locator = (By.XPATH, '//table[@class="table table-hover"]/tbody/tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('page=(\d+?)&', url)[0]

    if int(cnum) != num:
        val = driver.find_element_by_xpath('//table[@class="table table-hover"]/tbody/tr[1]//a').get_attribute('href')[
              -12:]

        url = re.sub('page=(\d+?)&', 'page=%s&' % num, url)
        driver.get(url)

        locator = (By.XPATH, '//table[@class="table table-hover"]/tbody/tr[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', class_='table table-hover')
    trs = div.find_all('tr')[1:]
    for tr in trs:
        tds = tr.find_all('td')
        href = tds[0].a['href']
        name = tds[0].a.get_text()

        if 'wsjj_xq' in url:
            ggend_time=tds[1].get_text()
            ggstart_time='kong'
            info={'ggend_time':ggend_time}
            info=json.dumps(info,ensure_ascii=False)
        else:
            ggstart_time = tds[1].get_text()
            info=None

        if 'http' in href:
            href = href
        else:
            href = 'http://fwgs.sinograin.com.cn' + href

        tmp = [name, ggstart_time, href,info]

        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//table[@class="table table-hover"]/tbody/tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        total = driver.find_element_by_xpath('//li[@class="last"]/a').get_attribute('href')
        total = re.findall('page=(\d+?)&', total)[0]
    except:
        driver.find_element_by_xpath('//table[@class="table table-hover"]/tbody[count(tr)>1]')
        total=1
    driver.quit()


    return int(total)



def f3(driver, url):

    driver.get(url)
    locator = (By.XPATH, '//div[@class="content"][string-length()>10] ')
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

    div = soup.find('div', class_="content")

    return div


data = [
    ["qy_zhaobiao_gg", "http://fwgs.sinograin.com.cn/more_list.html?page=1&q%5Bs%5D=id+desc&t=search_products&type=article_zbgg",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_zhongbiaohx_gg", "http://fwgs.sinograin.com.cn/more_list.html?page=1&q%5Bs%5D=id+desc&t=search_products&type=article_jggg",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_zhongbiao_jingjia_gg", "http://fwgs.sinograin.com.cn/more_list.html?page=1&q%5Bs%5D=id+desc&t=search_products&type=wsjj_jg",["name", "ggstart_time", "href", "info"], add_info(f1,{"zbfs":"网上竞价"}), f2],
    ["qy_zhaobiao_jingjia_gg", "http://fwgs.sinograin.com.cn/more_list.html?page=1&q%5Bs%5D=id+desc&t=search_products&type=wsjj_xq",["name", "ggstart_time", "href", "info"], add_info(f1,{"zbfs":"网上竞价"}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="中国储备粮管理集团", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch3", "fwgs_sinograin_com_cn"],headless=False,num=1)

    pass