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

from zhulong4.util.etl import est_html, est_meta, add_info,est_meta_large

_name_ = "www_sztc_com"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='lb-link']/ul[1]/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        locator = (By.XPATH, "//div[@class='pag-txt']/em[2]")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='lb-link']/ul[1]/li[1]/a").get_attribute('href')[-15:]
        if "index_" not in url:
            s = "index_%d" % (num) if num > 1 else "index"
            url = re.sub("index", s, url)
        elif num == 1:
            url = re.sub("index_[0-9]*", "index", url)
        else:
            s = "index_%d" % (num) if num > 1 else "index"
            url = re.sub("index_[0-9]*", s, url)
        driver.get(url)

        locator = (By.XPATH, "//div[@class='lb-link']/ul[1]/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("div", class_='lb-link')
    uls = div.find_all('ul')
    data = []
    for ul in uls:
        lis = ul.find_all('li')
        for li in lis:
            a = li.find("a")
            try:
                title = a['title'].strip()
            except:
                title = li.find('span', class_='bidLink').text.strip()
            link = a["href"]
            if 'http' in link:
                href = link
            else:
                href = 'http://www.sztc.com/' + link

            span = li.find("span", class_='bidDate').text.strip()
            tmp = [title, span, href]
            data.append(tmp)
            # f = f3(driver, href)
            # print(f)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='lb-link']/ul[1]/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='pag-txt']/em[last()]")
        num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@class='StdInputTable'] | //div[@class='mbox lpInfo']")
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
    div = soup.find('table', class_='StdInputTable')
    if div == None:
        div = soup.find('div', class_='mbox lpInfo')
    return div


data = [
    ["qy_zhaobiao_gg",
     "http://www.sztc.com/bidBulletin/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qy_zhaobiao_wuzi_gg",
     "http://www.sztc.com/bulkmaterialBulletin/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'大宗物资公告'}), f2],

    ["qy_zgys_gg",
     "http://www.sztc.com/preBulletin/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ####
    ["qy_biangeng_gg",
     "http://www.sztc.com/changeBulletin/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qy_gqita_zhong_liu_gg",
     "http://www.sztc.com/preBidBulletin/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qy_yucai_gg",
     "http://www.sztc.com/purchaseNotice/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="深圳国际", **args)
    est_html(conp, f=f3, **args)



# qy_zhaobiao_gg跑不完,f1数据获取不全，一次性跑不完
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang3", "www_sztc_com"])

    # driver = webdriver.Chrome()
    # url = "http://www.sztc.com/bidBulletin/index.jhtml"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "http://www.sztc.com/bidBulletin/index.jhtml"
    # driver.get(url)
    # for i in range(3, 5):
    #     df=f1(driver, i)
    #     print(df.values)
    #     for i in df[2].values:
    #         f = f3(driver, i)
    #         print(f)