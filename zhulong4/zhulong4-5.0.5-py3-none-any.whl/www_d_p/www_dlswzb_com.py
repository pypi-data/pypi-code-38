import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json

import time

from zhulong.util.etl import est_html, est_meta, add_info,est_meta_large

_name_ = "www_dlswzb_com"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='catlist']/ul/form[last()]/li/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        cnum = int(re.findall(r'page=(\d+)', url)[0])
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='catlist']/ul/form[1]/li/a").get_attribute('href')[-15:]
        tar = driver.find_element_by_xpath("//div[@class='catlist']/ul/form[last()]/li/a").get_attribute('href')[-15:]
        if 'page' not in url:
            s = '?page=%d' % (num) if num > 1 else "?page=1"
            url += s
        elif num == 1:
            url = re.sub("page=[0-9]*", "page=1", url)
        else:
            s = "page=%d" % (num) if num > 1 else "page=1"
            url = re.sub("page=[0-9]*", s, url)
        driver.get(url)

        locator = (By.XPATH, "//div[@class='catlist']/ul/form[1]/li/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 40).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, "//div[@class='catlist']/ul/form[last()]/li/a[not(contains(@href, '%s'))]" % tar)
        WebDriverWait(driver, 40).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("div", class_='catlist').ul
    lis = div.find_all('form')
    data = []
    for li in lis:
        li = li.find('li', class_='catlist_li')
        a = li.find("a", id='stitle')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://www.dlswzb.com/' + link
        span = li.find("span", class_='f_r px11 f_gray').text.strip()
        font = li.find_all("span")[-1].text.strip()
        ft = {'diqu': font}
        info = json.dumps(ft, ensure_ascii=False)
        tmp = [title, span, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='catlist']/ul/form[1]/li/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='pages']/a[last()-1]")
        num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='left_box']")
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
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_='left_box')
    return div


data = [
    ["qy_zhaobiao_gongcheng_gg",
     "http://www.dlswzb.com/gongcheng/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'工程'}), f2],

    ["qy_zhaobiao_huowu_gg",
     "http://www.dlswzb.com/huowu/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'货物'}), f2],

    ["qy_zhaobiao_fuwu_gg",
     "http://www.dlswzb.com/fuwu/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'服务'}), f2],

    ["qy_zhongbiao_gg",
     "http://www.dlswzb.com/zhongbiao/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="国家电投", **args, interval_page=100)
    est_html(conp, f=f3, **args)


# 页数太多，应加大线程数，而且网页加载慢,一次性跑不完
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang3", "www_dlswzb_com"],pageloadtimeout=180,pageLoadStrategy="none")

    # driver = webdriver.Chrome()
    # url = "http://www.dlswzb.com/huowu/"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "http://www.dlswzb.com/huowu/"
    # driver.get(url)
    # for i in range(46, 48):
    #     df=f1(driver, i)
    #     print(df.values)
