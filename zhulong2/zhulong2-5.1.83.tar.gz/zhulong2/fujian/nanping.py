import json
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

from zhulong2.util.etl import est_tbs, est_meta, est_html, gg_existed, est_gg, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hefei.gov.cn/jyxx/002001/002001002/moreinfo_jyxx.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_ = 'fujian_nanping'


def f1(driver, num):
    locator = (By.XPATH, '//ul[@id="resources"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url

    cnum = re.findall('&page=(\d+)$', url)[0]

    main_url = url.rsplit('=', maxsplit=1)[0]

    if int(cnum) != num:
        val = driver.find_element_by_xpath('//ul[@id="resources"]/li[1]/a').get_attribute('href').rsplit(
            '/', maxsplit=1)[1]

        url = main_url + '=%s' % num

        driver.get(url)

        locator = (By.XPATH, '//ul[@id="resources"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', id='resources')
    lis = div.find_all('li')
    for li in lis:
        href = li.a['href']
        name = li.a.get_text()
        ggstart_time = li.find('span', class_='time').get_text()

        if 'http' in href:
            href = href
        else:
            href = "http://www.np.gov.cn" + href

        tmp = [name,  ggstart_time,href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None

    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@id="resources"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('//div[@class="page"]/a[last()-2]').text.strip()

    total=int(page)

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@id="Zoom"][string-length()>10]')

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

    div = soup.find('div',id="Zoom")

    return div


data = [
    ###包含中标,流标
    ["zfcg_zhongbiao_gg", "http://www.np.gov.cn/cms/sitemanage/index.shtml?siteId=100379225526970000&page=1", ['name', 'ggstart_time', 'href', 'info'],f1, f2],
    ["zfcg_zhaobiao_gg", "http://www.np.gov.cn/cms/sitemanage/index.shtml?siteId=100379225585760000&page=1", ['name', 'ggstart_time', 'href', 'info'],f1, f2],
    ["zfcg_zhaobiao_danyilaiyuan_gg", "http://www.np.gov.cn/cms/sitemanage/index.shtml?siteId=100379225605360000&page=1", ['name', 'ggstart_time', 'href', 'info'],add_info(f1,{"zbfs":"单一来源"}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="福建省南平市", **args)
    est_html(conp, f=f3, **args)

if __name__ == '__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "lch", "fujian_nanping"]

    work(conp=conp)