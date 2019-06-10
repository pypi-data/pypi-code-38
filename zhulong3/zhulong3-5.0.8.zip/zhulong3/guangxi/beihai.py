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

_name_ = "guangxi_beihai"


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="bhdh_Box1"][1]/ul/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        if 'index' not in url:
            cnum = 1
        else:
            cnum = int(re.findall(r'index_(\d+)', url)[0])
            cnum += 1
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath('//div[@class="bhdh_Box1"][1]/ul/li[1]/a').get_attribute('href')[-30:]

        if "index" not in url:
            s = "index_%d.html" % (num-1) if num > 1 else "index.html"
            url = url + s
        elif num == 1:
            url = re.sub("index_[0-9]*", "index", url)
        else:
            s = "index_%d" % (num-1) if num > 1 else "index"
            url = re.sub("index_[0-9]*", s, url)
            # print(cnum)
        driver.get(url)
        locator = (By.XPATH, "//div[@class='bhdh_Box1'][1]/ul/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    divs = soup.find_all("div", class_='bhdh_Box1')
    data = []
    for div in divs:
        ul = div.find("ul", class_='bhdh_List')
        lis = ul.find_all('li')
        for li in lis:
            a = li.find('a')
            try:
                title = a['title'].strip()
            except:
                title = a.text.strip()
            span = li.find("span").text.strip()
            span = re.findall(r'(\d+-\d+-\d+)', span)[0]
            link = a["href"]
            if 'http' in link:
                href = link
            else:
                href = 'http://xxgk.beihai.gov.cn/' + link
            tmp = [title, span, href]
            data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="bhdh_Box1"][1]/ul/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        try:
            locator = (By.XPATH, '//a[@id="pagenav_nextgroup"]')
            li = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')
            num = re.findall(r'index_(\d+)', li)[0]
        except:
            locator = (By.XPATH, '//div[@class="fenye"]/a[last()-1]')
            num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    except:
        num = 1
    total = int(num)
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='xlyNews']")
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
    div = soup.find('div', class_='xlyNews')
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


data = [

    ["gcjs_zhaobiao_gg", "http://xxgk.beihai.gov.cn/bhszfhcxjsj/jsztbxx/zbgg/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_zhongbiaohx_gg", "http://xxgk.beihai.gov.cn/bhszfhcxjsj/jsztbxx/zbhxrgs/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_zhongbiao_gg", "http://xxgk.beihai.gov.cn/bhszfhcxjsj/jsztbxx/zbjggg/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_gqita_gg", "http://xxgk.beihai.gov.cn/bhszfhcxjsj/wyglztbxx/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gglx':'物业管理招投标信息'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广西省北海市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang2", "guangxi_beihai"])

    # driver = webdriver.Chrome()
    # url = "http://xxgk.beihai.gov.cn/bhszfhcxjsj/jsztbxx/zbjggg/"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "http://xxgk.beihai.gov.cn/bhszfhcxjsj/jsztbxx/zbjggg/"
    # driver.get(url)
    # for i in range(1, 6):
    #     df=f1(driver, i)
    #     print(df.values)
