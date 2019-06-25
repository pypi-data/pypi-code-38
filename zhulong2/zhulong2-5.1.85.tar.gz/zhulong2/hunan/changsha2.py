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

from zhulong2.util.etl import est_tbs, est_meta, est_html, est_gg, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hengyang.gov.cn/jyxx/jsgc/zbgg_64796/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_ = 'hunan_changsha2'


def f1(driver, num):
    locator = (By.XPATH,'//div[@class="list list_1 list_2"]//li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url = driver.current_url
    if 'index.html' in url:
        cnum=1
    else:
        cnum=int(re.findall('index_(\d+).html',url)[0])+1

    if int(cnum) != num:
        val =driver.find_element_by_xpath('//div[@class="list list_1 list_2"]//li[1]//a').get_attribute('href').rsplit('/', maxsplit=1)[1]

        if num ==1:
            s='index.html'
        else:
            s='index_%s.html'%(num-1)
        url_=re.sub('index_{0,1}.html',s,url)
        driver.get(url_)

        locator = (By.XPATH,
                   '//div[@class="list list_1 list_2"]//li[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    divs = soup.find('div', class_='list list_1 list_2').find_all('li',class_='')

    for div in divs:
        name = div.find('a').get_text()
        href = div.find('a')['href'].strip('.')
        ggstart_time=div.find('span',class_='date').get_text()

        if 'http' in href:
            href = href
        else:
            href = url.rsplit('/',maxsplit=1)[0] + href
        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df


def f2(driver):
    locator = (By.XPATH,'//div[@class="list list_1 list_2"]//li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('//div[@class="div_cutPage"]//a[last()]').get_attribute('href')
    total = re.findall('index_(\d+).html', page)[0].strip()
    total = int(total)+1
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="pages_content"][string-length()>50]')
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
    div = soup.find('div', class_="pages_content").parent

    return div


data = [

    ["zfcg_zhaobiao_gg","http://www.changsha.gov.cn/xxgk/szfxxgkml/czxx/zfcg2/zbgg/index.html",["name", "ggstart_time", "href", 'info'], f1, f2],
    ["zfcg_zhongbiao_gg","http://www.changsha.gov.cn/xxgk/szfxxgkml/czxx/zfcg2/zbgg1/index.html",["name", "ggstart_time", "href", 'info'], f1, f2],
    ["zfcg_gqita_da_bian_gg","http://www.changsha.gov.cn/xxgk/szfxxgkml/czxx/zfcg2/qtgg/index.html",["name", "ggstart_time", "href", 'info'], f1, f2],

]

def work(conp, **args):
    est_meta(conp, data=data, diqu="湖南省长沙市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "lch", "hunan_changsha2"]

    work(conp=conp, pageloadtimeout=80, pageloadstrategy='none',headless=False,num=1)