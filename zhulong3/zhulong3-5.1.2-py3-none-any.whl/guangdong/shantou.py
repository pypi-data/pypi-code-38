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

from zhulong3.util.etl import est_tbs, est_meta, est_html, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url = "http://www.fzztb.com/CmsPortalWeb/main/project.xhtml"
# driver = webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_ = 'guangdong_shantou'


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="a_lay"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('page=(\d+)$', url)[0]

    if cnum != str(num):
        val = driver.find_element_by_xpath('//div[@class="a_lay"]//tr[2]//a').get_attribute('href')[-20:]
        url = url.rsplit('=', maxsplit=1)[0] + '=%s' % num
        driver.get(url)
        locator = (By.XPATH, '//div[@class="a_lay"]//tr[2]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find('div', class_='a_lay').find_all('tr')[1:]

    for tr in trs:
        tds = tr.find_all('td')
        href = tr.find('a')['href'].strip('.')
        name = tds[1].get_text()
        address = re.split(' +', name, maxsplit=1)[0].strip()
        name = re.split(' +', name, maxsplit=1)[1].strip()

        ggstart_time = tds[-1].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.stjs.org.cn/zbtb/' + href
        info={'diqu':address}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time,href, info]

        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="a_lay"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//td[2][@class="paginator"]/a[last()]').get_attribute('href')

    total = re.findall("page=(\d+)", total)[0]
    total = int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//div[@class="b_tive"][string-length()>10]')

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

    div = soup.find('div', class_="b_tive")

    return div


data = [


    ["gcjs_zhaobiao_gg", "http://www.stjs.org.cn/zbtb/zbtb_zbgg.aspx?page=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://www.stjs.org.cn/zbtb/zbtb_zbgs.aspx?page=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg", "http://www.stjs.org.cn/zbtb/zbtb_zhongbiaogg.aspx?page=1",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_richeng_gg", "http://www.stjs.org.cn/zbtb/zbtb_rcap.aspx?page=1",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"日程安排"}), f2],
    ["gcjs_dayi_gg", "http://www.stjs.org.cn/zbtb/zbtb_wsdy.aspx?page=1",["name", "ggstart_time", "href", "info"], f1, f2],

]

def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省汕头市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "guangdong_shantou"],headless=False,num=1)