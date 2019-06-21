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

from zhulong4.util.etl import est_html, est_meta, add_info

_name_ = "www_ngecc_com"


def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='news_ul']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        locator = (By.XPATH, "//li[@class='thisclass']/a")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='news_ul']/li[1]/a").get_attribute('href')[-15:]
        if "PageNo" not in url:
            s = "&TotalResult=190&PageNo=%d" % (num) if num > 1 else "&TotalResult=190&PageNo=1"
            url += s
        elif num == 1:
            url = re.sub("PageNo=[0-9]*", "PageNo=1", url)
        else:
            s = "PageNo=%d" % (num) if num > 1 else "PageNo=1"
            url = re.sub("PageNo=[0-9]*", s, url)
        driver.get(url)

        locator = (By.XPATH, "//ul[@class='news_ul']/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("ul", class_='news_ul')
    lis = div.find_all('li')
    data = []
    for li in lis:
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://www.ngecc.com' + link

        span = li.find('span').text.strip()
        try:
            span = re.findall(r'(\d+-\d+-\d+)', span)[0]
        except:
            span = '-'
        tmp = [title, span, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//ul[@class='news_ul']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//ul[@class='pagelist']/li[last()]/a")
        href = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')
        num = re.findall(r'PageNo=(\d+)', href)[0]
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='news-content']")
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
    div = soup.find('div', id='news-content')
    return div



data = [
    ["qy_zhaobiao_gg",
     "http://www.ngecc.com/plus/list.php?tid=172&TotalResult=190&PageNo=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="中国黄金集团有限公司", **args)
    est_html(conp, f=f3, **args)



if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang3", "www_ngecc_com"])

    # driver = webdriver.Chrome()
    # url = "http://www.ngecc.com/plus/list.php?tid=172&TotalResult=190&PageNo=1"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "http://www.ngecc.com/plus/list.php?tid=172&TotalResult=190&PageNo=1"
    # driver.get(url)
    # for i in range(8, 11):
    #     df=f1(driver, i)
    #     print(df.values)
    #     for i in df[2].values:
    #         f = f3(driver, i)
    #         print(f)