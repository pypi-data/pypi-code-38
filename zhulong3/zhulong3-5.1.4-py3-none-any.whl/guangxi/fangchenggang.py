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

import json

import time

from zhulong3.util.etl import est_html, est_meta, add_info

_name_ = "guangxi_fangchenggang"


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="news_r_top_lb"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, '//span[@class="cpb"]')
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath('//div[@class="news_r_top_lb"]/li[1]/a').get_attribute('href')[-10:]

        driver.execute_script("javascript:__doPostBack('cg_page','{}')".format(num))
        locator = (By.XPATH, "//div[@class='news_r_top_lb']/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("div", class_='news_r_top_lb')
    lis = div.find_all("li")
    data = []
    for li in lis:
        a = li.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        span = a.find("span").text.strip()

        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://www.fcgzbzj.cn/' + link
        tmp = [title, span, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="news_r_top_lb"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, '//div[@id="cg_page"]/a[last()]')
        li = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')
        num = re.findall(r'(\d+)', li)[0]
    except:
        num = 1
    total = int(num)
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='news_r']")
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
    div = soup.find('div', class_='news_r')
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


data = [
    #
    ["gcjs_zhongbiao_gg", "http://www.fcgzbzj.cn/list.aspx?type=89",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_gg", "http://www.fcgzbzj.cn/list.aspx?type=90",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_zhongbiaohx_gg", "http://www.fcgzbzj.cn/list.aspx?type=91",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_gqita_liu_kong_gg", "http://www.fcgzbzj.cn/list.aspx?type=93",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广西省防城港市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang2", "guangxi_fangchenggang"])

    # driver = webdriver.Chrome()
    # url = "http://www.fcgzbzj.cn/list.aspx?type=93"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "http://www.fcgzbzj.cn/list.aspx?type=93"
    # driver.get(url)
    # for i in range(1, 6):
    #     df=f1(driver, i)
    #     print(df.values)
