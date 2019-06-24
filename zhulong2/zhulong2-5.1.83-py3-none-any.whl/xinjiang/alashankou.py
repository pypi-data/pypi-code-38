import random

import pandas as pd
import re

import requests
from lxml import etree
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

from zhulong2.util.etl import est_html, est_meta, add_info

_name_ = "xinjiang_alashankou"


def f1(driver, num):
    locator = (By.XPATH, "//table[@class='publicTable']/tbody/tr[2]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//td[@id='fanye23633']")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = re.findall(r'(\d+)/', cnum)[0]
    except:
        cnum = 1
    url = driver.current_url
    if num != int(cnum):
        val = \
        driver.find_element_by_xpath("//table[@class='publicTable']/tbody/tr[2]/td/a").get_attribute('href').rsplit('/',
                                                                                                                    maxsplit=1)[
            1]
        driver.find_element_by_xpath("//input[@class='defaultInputStyle']").clear()
        driver.find_element_by_xpath("//input[@class='defaultInputStyle']").send_keys(num)
        driver.find_element_by_xpath("//input[@class='defaultButtonStyle']").click()
        locator = (By.XPATH, "//table[@class='publicTable']/tbody/tr[2]/td/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    tbody = soup.find("table", class_='publicTable').tbody
    trs = tbody.find_all("tr")
    data = []
    for tr in trs[1:]:
        a = tr.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        href = a['href'].strip()
        if 'http' in href:
            link = href
        else:
            href = href.split('/', maxsplit=2)[-1]
            link = 'http://www.alsk.gov.cn/' + href
        span = tr.find('td', class_='date').text.strip()
        tmp = [title, span, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//table[@class='publicTable']/tbody/tr[2]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    driver.find_element_by_xpath("//a[@class='Next'][last()]").click()
    locator = (By.XPATH, "//td[@id='fanye23633']")
    str_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'/(\d+)', str_1)[0]
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//form[@name='_newscontent_fromname'][string-length()>10]")
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
    div = soup.find('form', attrs={'name': '_newscontent_fromname'})
    return div


data = [
    ["zfcg_gqita_zhao_zhong_gg",
     "http://www.alsk.gov.cn/zwgk/cgzb.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="新疆省阿拉山口市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "alashankou"])
