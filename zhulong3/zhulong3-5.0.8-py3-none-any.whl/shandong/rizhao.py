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

_name_ = 'shandong_rizhao'


def f1(driver, num):
    locator = (By.XPATH, '//table[@class="ListTable"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('page=(\d+)$', url)[0]

    if cnum != str(num):
        val = driver.find_element_by_xpath('//table[@class="ListTable"]//tr[2]//a').get_attribute('href')[-15:]

        url = url.rsplit('=', maxsplit=1)[0] + '=%s' % num
        driver.get(url)

        locator = (By.XPATH, '//table[@class="ListTable"]//tr[2]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find('table', class_="ListTable").find_all('tr')[1:]
    for tr in trs:
        tds = tr.find_all('td')
        index_num = tds[1].get_text()
        href = tds[2].a['href']
        name = tds[2].a.get_text().strip()
        company = tds[3].get_text().strip()
        ggend_time = tds[5].get_text().strip()
        ggstart_time = tds[4].get_text().strip()

        if 'http' in href:
            href = href
        else:
            href = 'http://222.133.187.138' + href
        info={'index_num':index_num,'company':company,'ggend_time':ggend_time}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time, href,info]
        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df


def f4(driver, num):
    locator = (By.XPATH, '//table[@class="ListTable"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('page=(\d+)$', url)[0]

    if cnum != str(num):
        val = driver.find_element_by_xpath('//table[@class="ListTable"]//tr[2]//a').get_attribute('href')[-15:]

        url = url.rsplit('=', maxsplit=1)[0] + '=%s' % num
        driver.get(url)

        locator = (By.XPATH, '//table[@class="ListTable"]//tr[2]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find('table', class_="ListTable").find_all('tr')[1:]
    for tr in trs:
        tds = tr.find_all('td')
        index_num = tds[1].get_text()
        href = tds[2].a['href']
        name = tds[2].a.get_text().strip()
        ggend_time = tds[4].get_text().strip()
        ggstart_time = tds[3].get_text().strip()
        zb_company = tds[5].get_text().strip()
        zb_money = tds[6].get_text().strip()

        if 'http' in href:
            href = href
        else:
            href = 'http://222.133.187.138' + href
        info={'index_num':index_num,'zb_company':zb_company,'ggend_time':ggend_time,"zb_money":zb_money}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time, href,info]
        data.append(tmp)
    df = pd.DataFrame(data=data)


    return df


def f2(driver):
    locator = (By.XPATH, '//table[@class="ListTable"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//div[@class="digg"]/a[last()-1] | //div[@id="divPager"]/a[last()-1]').text
    driver.quit()
    total=int(total)
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//div[@class="text"][string-length()>10]')

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

    div = soup.find('div', class_="text")

    return div


data = [

    ##包含招标,变更
    ["gcjs_zhaobiao_gg", "http://222.133.187.138/zbgg_list.aspx?category_id=1&page=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ##包含中标,流标
    ["gcjs_zhongbiaohx_gg", "http://222.133.187.138/zbgs_list.aspx?category_id=2&page=1",["name", "ggstart_time", "href", "info"], f4, f2],


]

def work(conp, **args):
    est_meta(conp, data=data, diqu="山东省日照市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "shandong_rizhao"])