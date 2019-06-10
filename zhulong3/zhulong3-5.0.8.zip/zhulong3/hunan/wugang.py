import time

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
import requests
import json

from zhulong3.util.etl import est_tbs, est_meta, est_html

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url = "http://www.fzztb.com/CmsPortalWeb/main/project.xhtml"
# driver = webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_ = 'hunan_wugang'

def f1(driver, num):
    locator = (By.XPATH, '(//tr[@class="tr22"])[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall(r'page=(\d+?)&', url)[0]

    if cnum != str(num):
        val = driver.find_element_by_xpath('(//tr[@class="tr22"])[2]//a').get_attribute('href')[-35:-20]

        url = re.sub('page=\d+?&', 'page=%s&' % num, url)
        driver.get(url)

        locator = (By.XPATH, '(//tr[@class="tr22"])[2]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find_all('tr', class_='tr22')[1:-1:2]
    for tr in trs:
        href = tr.find('a')['href']
        name = tr.find('a')['title']
        ggstart_time = tr.find_all('td')[-1].font.get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.wgjszbw.com/' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '(//tr[@class="tr22"])[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath('(//tr[@class="tr22"])[last()]/td').text
    total = int(re.findall(r'共(.+?)页', total)[0].strip())
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//td[@class="newscontent"][string-length()>10]')

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    time.sleep(0.1)
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

    div = soup.find('td', class_="newscontent")

    return div


data = [

    #包含招标,补充
    ["gcjs_gqita_zhao_da_gg", "http://www.wgjszbw.com/list.asp?idd=217&page=1&classid=217",[ "name", "ggstart_time", "href", "info"], f1, f2],
    #包含中标,变更
    ["gcjs_zhongbiaohx_gg", "http://www.wgjszbw.com/list.asp?idd=409&page=1&classid=409",[ "name", "ggstart_time", "href", "info"], f1, f2],
    #包含流标,变更
    ["gcjs_gqita_bian_liu_gg", "http://www.wgjszbw.com/list.asp?idd=216&page=1&classid=216",[ "name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖南省武冈市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "hunan_wugang"])