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

_name_ = 'hunan_huaihua'

def f1(driver, num):
    locator = (By.XPATH, '//div[@class="list"]/a[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall(r'current_page=(\d+)$', url)[0]

    if cnum != str(num):
        val = driver.find_element_by_xpath('//div[@class="list"]/a[1]').get_attribute('href')[-30:]
        url = url.rsplit('=', maxsplit=1)[0] + '=%s' % num
        driver.get(url)

        locator = (By.XPATH, '//div[@class="list"]/a[1][not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find('div', class_='list').find_all('a')
    for tr in trs:

        href = tr['href'].strip('.')
        name = tr.find('span',class_='title').get_text()
        ggstart_time = tr.find('span', class_='time').get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.hhztb.com' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="list"]/a[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        total = driver.find_element_by_xpath('//select[@class="set_page_go"]/option[last()]').get_attribute('value')
        total = int(total)
    except:
        total=1
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
           '//div[@id="article_show_html"][string-length()>10]')

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

    div = soup.find('div', id="article_show_html")

    return div


data = [

    ["gcjs_zhaobiao_gg", "http://www.hhztb.com/index.php?monxin=article.show_article_list&type=94&current_page=1",[ "name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_biangeng_gg", "http://www.hhztb.com/index.php?monxin=article.show_article_list&type=95&current_page=1",[ "name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_dayi_gg", "http://www.hhztb.com/index.php?monxin=article.show_article_list&type=96&current_page=1",[ "name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_liubiao_gg", "http://www.hhztb.com/index.php?monxin=article.show_article_list&type=97&current_page=1",[ "name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_kongzhijia_gg", "http://www.hhztb.com/index.php?monxin=article.show_article_list&type=98&current_page=1",[ "name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://www.hhztb.com/index.php?monxin=article.show_article_list&type=100&current_page=1",[ "name", "ggstart_time", "href", "info"], f1, f2],
    ##包含中标,流标
    ["gcjs_zhongbiaohx_2_gg", "http://www.hhztb.com/index.php?monxin=article.show_article_list&type=99&current_page=1",[ "name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖南省怀化市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "hunan_huaihua"],headless=False,num=1)