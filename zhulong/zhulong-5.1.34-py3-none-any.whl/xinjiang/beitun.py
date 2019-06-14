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

from zhulong.util.etl import est_tbs, est_meta, est_html, gg_existed, est_gg, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hefei.gov.cn/jyxx/002001/002001002/moreinfo_jyxx.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_ = 'beitun'


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="docuContent listul"]/ul/li[1]/a[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    if 'index.shtml' in url:
        cnum=1
    else :
        cnum = re.findall('index_(.+)\.shtml',url)[0]

    main_url = url.rsplit('index', maxsplit=1)[0]
    if int(cnum) != num:

        val = driver.find_element_by_xpath('//div[@class="docuContent listul"]/ul/li[1]/a[1]').get_attribute('href')[-20:-5]
        if num == 1:
            url = main_url + 'index.shtml'
        else:
            url = main_url + 'index_%s.shtml' % num

        driver.get(url)

        locator = (By.XPATH, '//div[@class="docuContent listul"]/ul/li[1]/a[1][not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lis = soup.find('div', class_='docuContent listul').find_all('li')

    for li in lis:

        tds = li.find_all('a')
        href = tds[0]['href']
        name = tds[0].get_text()

        ggstart_time = tds[1].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.bts.gov.cn' + href

        tmp = [name, ggstart_time,href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="docuContent listul"]/ul/li[1]/a[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        page = driver.find_element_by_xpath('//table[@class="noBorder"]//td').text
        total = re.findall('/(\d+)页', page)[0]
        total = int(total)
    except:

        total=1

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="detailPar"]')

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

    div = soup.find('div',class_="pargraph")

    return div


data = [

    ["gcjs_zhaobiao_gg", "http://www.bts.gov.cn/gk/zbcg/gcjs/zbgg/index.shtml", ['name', 'ggstart_time', 'href', 'info'],f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://www.bts.gov.cn/gk/zbcg/gcjs/zbgs/index.shtml", ['name', 'ggstart_time', 'href', 'info'],f1, f2],

    ["zfcg_zhaobiao_gg", "http://www.bts.gov.cn/gk/zbcg/zfcg/cggg/index.shtml", ['name', 'ggstart_time', 'href', 'info'],f1, f2],
    ["zfcg_zhaobiao_danyilaiyuan_gg", "http://www.bts.gov.cn/gk/zbcg/zfcg/dylygs/index.shtml", ['name', 'ggstart_time', 'href', 'info'],add_info(f1,{"zbfs":"单一来源"}), f2],
    ["zfcg_biangeng_gg", "http://www.bts.gov.cn/gk/zbcg/zfcg/bggg/index.shtml", ['name', 'ggstart_time', 'href', 'info'],f1, f2],
    ["zfcg_zhongbiao_gg", "http://www.bts.gov.cn/gk/zbcg/zfcg/zbgs/index.shtml", ['name', 'ggstart_time', 'href', 'info'],f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="新疆省北屯市", **args)
    est_html(conp, f=f3, **args)

if __name__ == '__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "xinjiang", "beitun"]

    work(conp=conp,pageLoadStrategy = "none")