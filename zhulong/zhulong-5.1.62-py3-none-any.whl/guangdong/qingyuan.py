import json

import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write, db_command, db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, add_info, est_gg

# driver=webdriver.Chrome()
# url="http://www.bygzjy.cn/f/trade/annogoods/list?selectedProjectType=3"
# driver.get(url)

_name_ = 'qingyuan'


def f1(driver, num):
    locator = (By.XPATH, '//table[@class="newtable"]//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = int(driver.find_element_by_xpath('//span[@class="current"]').text)

    if cnum != num:
        val = driver.find_element_by_xpath(
            '//table[@class="newtable"]//tr[1]//a').get_attribute('href')[-30:-5]

        driver.execute_script("javascript:goPage(%s)" % num)

        locator = (
            By.XPATH, "//table[@class='newtable']//tr[1]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("table", class_="newtable")
    dls = div.find_all("tr")[:-2]
    data = []
    for dl in dls:

        name = dl.find('a').get_text().strip().split('\t')[-1].strip()
        href = dl.find('a')['href']
        ggstart_time = dl.find_all('td')[1].get_text().strip()
        info = None

        if 'http' in href:
            href = href
        else:
            href = 'https://www.qyggzy.cn' + href

        tmp = [name, ggstart_time, href, info]

        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, "//table[@class='newtable']//tr[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//div[@class="scott"]/a[last()]').get_attribute('href')
    total=re.findall('javascript:goPage\((\d+)\)',total)[0]

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="maincont"][string-length()>100]')
    WebDriverWait(
        driver, 10).until(
        EC.presence_of_all_elements_located(locator))

    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 5:
            break

    # f3 情况1
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_='maincont')

    return div


data = [

    ["gcjs_zhaobiao_gg",
     "https://www.qyggzy.cn/webIndex/newsLeftBoard/0102/010201",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_da_bian_gg",
     "https://www.qyggzy.cn/webIndex/newsLeftBoard/0102/010205",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "https://www.qyggzy.cn/webIndex/newsLeftBoard/0102/010202",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "https://www.qyggzy.cn/webIndex/newsLeftBoard/0102/010210",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["zfcg_zhaobiao_gg",
     "https://www.qyggzy.cn/webIndex/newsLeftBoard/0103/010304",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_gqita_da_bian_gg",
     "https://www.qyggzy.cn/webIndex/newsLeftBoard/0103/010305",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiaohx_gg",
     "https://www.qyggzy.cn/webIndex/newsLeftBoard/0103/010306",
     ["name", "ggstart_time", "href", "info"], f1, f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省清远市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(
        conp=[
            "postgres",
            "since2015",
            '192.168.3.171',
            "guangdong",
            "qingyuan"],
        headless=True,
        num=1,
        total=2)
