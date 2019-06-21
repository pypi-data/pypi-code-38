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

from zhulong4.util.etl import est_html, est_meta, add_info, est_meta_large

_name_ = "www_dlzb_com"


def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='gclist_ul listnew']/li[last()]/a[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        cnum = int(re.findall(r'-(\d+)\.html', url)[0])
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='gclist_ul listnew']/li[1]/a[1]").get_attribute('href')[-15:]
        tar = driver.find_element_by_xpath("//ul[@class='gclist_ul listnew']/li[last()]/a[1]").get_attribute('href')[-15:]
        if num == 1:
            url = re.sub("-[0-9]*\.html", "-1.html", url)
        else:
            s = "-%d.html" % (num) if num > 1 else "-1.html"
            url = re.sub("-[0-9]*\.html", s, url)
            # print(cnum)
        driver.get(url)
        time.sleep(1)
        locator = (By.XPATH, "//ul[@class='gclist_ul listnew']/li[1]/a[1][not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, "//ul[@class='gclist_ul listnew']/li[last()]/a[1][not(contains(@href, '%s'))]" % tar)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("ul", class_='gclist_ul listnew')
    lis = div.find_all('li')
    data = []
    for li in lis:
        a = li.find("a", class_='gccon_title')
        title = a.text.strip()
        link = a["href"]
        if ('http' in link) or ('https' in link):
            href = link
        else:
            href = 'https://www.dlzb.com/' + link

        span = li.find("span", class_='gc_date').text.strip()
        tmp = [title, span, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//ul[@class='gclist_ul listnew']/li[1]/a[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//div[@class='pages']/a[last()-1]")
    num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='content'][string-length()>40]")
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
    div = soup.find('div', class_='text')
    if div == None:
        div = soup.find('div', class_='t_area1')
        if div == None:
            div = soup.find('div', class_='po')
            if div == None:
                div = soup.find('div', id='content')
    return div


data = [
    ["qy_zhaobiao_gongcheng_gg",
     "https://www.dlzb.com/gongcheng/gongcheng-1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx':'工程'}), f2],

    ["qy_zhaobiao_huowu_gg",
     "https://www.dlzb.com/huowu/huowu-1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx':'货物'}), f2],

    ["qy_zhaobiao_fuwu_gg",
     "https://www.dlzb.com/fuwu/fuwu-1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx':'服务'}), f2],

    ["qy_zhongbiao_gg",
     "https://www.dlzb.com/zhongbiao/zhongbiao-1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="中国电力", **args)
    est_html(conp, f=f3, **args)


# 该网站需要登录才能看到更多数据，导致f1数据获取不全，故线程数应更多,一次性跑不完
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang3", "www_dlzb_com"],pageloadtimeout=60,pageLoadStrategy="none",num=30)

    # driver = webdriver.Chrome()
    # url = "https://www.dlzb.com/zhongbiao/zhongbiao-1.html"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "https://www.dlzb.com/zhongbiao/zhongbiao-1.html"
    # driver.get(url)
    # for i in range(13, 15):
    #     df=f1(driver, i)
    #     print(df.values)
