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

_name_ = 'shandong_dongying'


def f1(driver, num):
    locator = (By.XPATH, '//div[@id="Grid"]/table/tbody/tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//span[@class="t-state-active"]').text


    if cnum != str(num):
        val = driver.find_element_by_xpath('//div[@id="Grid"]/table/tbody/tr[1]//a').get_attribute('href')[-30:]

        input_ = driver.find_element_by_xpath('//div[@class="t-page-i-of-n"]/input')
        input_.click()
        input_.clear()
        input_.send_keys(num, Keys.ENTER)

        locator = (By.XPATH, '//div[@id="Grid"]/table/tbody/tr[1]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find('div', id="Grid").find_all('tr')[1:]
    for tr in trs:
        tds = tr.find_all('td')

        href = tds[0].a['href']
        name = tds[0].a['title']
        gg_type = tds[1].get_text()
        zbdl = tds[3].get_text().strip()
        jsdw = tds[4].get_text().strip()
        address = tds[5].get_text().strip()
        ggend_time = tds[6].get_text().strip()
        ggstart_time = tds[6].get_text().strip()

        if 'http' in href:
            href = href
        else:
            href = 'http://103.239.153.139:88' + href
        info={'gg_type':gg_type,'ggend_time':ggend_time,'zbdl':zbdl,'address':address,'jsdw':jsdw}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]

        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@id="Grid"]/table/tbody/tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath('//div[@class="t-page-i-of-n"]').text
    total = re.findall('共(.+)页', total)[0].strip()
    total=int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//div[@style="margin: auto;"]')

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

    div = soup.find('div', attrs={'style':re.compile('^margin: auto;$')})

    return div


data = [

    ##包含招标,变更
    ["gcjs_zhaobiao_gg", "http://103.239.153.139:88/dyztb/ZTB?flag=-1",["name", "ggstart_time", "href", "info"], f1, f2],
    ##包含中标,流标
    ["gcjs_zhongbiao_gg", "http://103.239.153.139:88/dyztb/ZTB?flag=2",["name", "ggstart_time", "href", "info"], f1, f2],

]

def work(conp, **args):
    est_meta(conp, data=data, diqu="山东省东营市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "shandong_dongying"],headless=False)