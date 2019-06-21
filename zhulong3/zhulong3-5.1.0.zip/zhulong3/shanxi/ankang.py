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

from zhulong3.util.etl import est_html, est_meta, add_info

_name_ = "shanxi_ankang"


def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='newslist ico03']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        locator = (By.XPATH, '//div[@id="AspNetPager1"]/table/tbody/tr/td/font[3]/b')
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='newslist ico03']/li[1]/a").get_attribute('href')[-15:]
        driver.execute_script("javascript:__doPostBack('AspNetPager1','{}')".format(num))

        locator = (By.XPATH, "//ul[@class='newslist ico03']/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("ul", class_='newslist ico03')
    lis = div.find_all('li')
    data = []
    for li in lis:
        span = li.find("span").extract().text.strip()
        try:
            font = li.find('font').extract().text.strip()
            font = re.findall(r'\[(.*)\]', font)[0]
        except:
            font = None
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()

        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://zbjy.ankang.cn/' + link
        ft = {'lx':font}
        info = json.dumps(ft,ensure_ascii=False)
        tmp = [title, span, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, "//ul[@class='newslist ico03']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@id='AspNetPager1']/table/tbody/tr/td/font[1]/b")
        num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='box_m']")
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
    div = soup.find('div', class_='m714 fr')
    div=div.find('div',class_='box_m')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://zbjy.ankang.cn/GongCheng.aspx?Pid=2&Xid=5",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://zbjy.ankang.cn/GongCheng.aspx?Pid=2&Xid=6",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="陕西省安康市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang2", "shanxi_ankang"],pageloadtimeout=120,pageLoadStrategy="none")

    # driver = webdriver.Chrome()
    # url = "http://zbjy.ankang.cn/GongCheng.aspx?Pid=2&Xid=5"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "http://zbjy.ankang.cn/GongCheng.aspx?Pid=2&Xid=5"
    # driver.get(url)
    # for i in range(3, 5):
    #     df=f1(driver, i)
    #     print(df.values)
