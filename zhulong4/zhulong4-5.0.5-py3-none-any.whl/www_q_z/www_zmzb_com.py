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

_name_ = "www_zmzb_com"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='lb-link']/ul[1]/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        locator = (By.XPATH, "//div[@class='pag-txt']/em[1]")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='lb-link']/ul[1]/li[1]/a").get_attribute('href')[-20:]
        tar = driver.find_element_by_xpath("//div[@class='lb-link']/ul[1]/li[last()]/a").get_attribute('href')[-20:]
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
        locator = (By.XPATH, "//div[@class='lb-link']/ul[1]/li[last()]/a[not(contains(@href, '%s'))]" % tar)
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
                href = 'http://www.zmzb.com/' + link
            span = li.find("span", class_='bidDate').text.strip()
            tmp = [title, span, href]
            data.append(tmp)
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
    locator = (By.XPATH, "//table[@class='StdInputTable'][string-length()>30] | //div[@class='ninfo-con'][string-length()>30]")
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
    div = soup.find('div', class_='mbox lpInfo')
    if not div:
        divs = soup.find_all('table', class_='StdInputTable')
        div = ''
        for d in divs:
            div+=str(d)
    return div


data = [
    ["qy_zhaobiao_huowu_gg",
     "http://www.zmzb.com/gghw/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'货物'}), f2],

    ["qy_zhaobiao_gongcheng_gg",
     "http://www.zmzb.com/gggc/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'工程'}), f2],

    ["qy_zhaobiao_fuwu_gg",
     "http://www.zmzb.com/ggff/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'服务'}), f2],
    ####
    ["qy_biangeng_huowu_gg",
     "http://www.zmzb.com/bggghw/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'货物'}), f2],

    ["qy_biangeng_gongcheng_gg",
     "http://www.zmzb.com/bggggc/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'工程'}), f2],

    ["qy_biangeng_fuwu_gg",
     "http://www.zmzb.com/bgggfw/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'服务'}), f2],
    ####
    ["qy_zhongbiaohx_huowu_gg",
     "http://www.zmzb.com/pbhw/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'货物'}), f2],

    ["qy_zhongbiaohx_gongcheng_gg",
     "http://www.zmzb.com/pbgc/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'工程'}), f2],

    ["qy_zhongbiaohx_fuwu_gg",
     "http://www.zmzb.com/pbjg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'服务'}), f2],
    ####
    ["qy_zhaobiao_xunjia_huowu_gg",
     "http://www.zmzb.com/xjgshw/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'货物','zbfs':'询价'}), f2],

    ["qy_zhaobiao_xunjia_gongcheng_gg",
     "http://www.zmzb.com/xjgsgc/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'工程','zbfs':'询价'}), f2],

    ["qy_zhaobiao_xunjia_fuwu_gg",
     "http://www.zmzb.com/xjgsfw/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'服务','zbfs':'询价'}), f2],

    ["qy_zhaobiao_xunjia_dianshang_gg",
     "http://www.zmzb.com/dsgg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'lx':'电商','zbfs':'询价'}), f2],
]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="中煤集团", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang3", "www_zmzb_com"],pageloadtimeout=120,pageLoadStrategy="none")

    # driver = webdriver.Chrome()
    # url = "http://www.zmzb.com/pbhw/index.jhtml"
    # driver.get(url)
    # f = f3(driver, 'http://cg.chinacoal.com:7002/b2b/web/two/indexinfoAction.do?actionType=showCgxjDetail&xjbm=E612AB351FE306A97E1B9190F55D3D3E')
    # print(f)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "http://www.zmzb.com/xjgshw/index.jhtml"
    # driver.get(url)
    # for i in range(3, 5):
    #     df=f1(driver, i)
    #     print(df.values)
    #     for j in df[2].values:
    #         f = f3(driver, j)
    #         print(f)