import json
import time

import pandas as pd
import re
import math
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# from zhulong.util.etl import est_tbs, est_meta, est_html, est_gg
from zhulong.util.etl import est_meta, est_html, est_gg, add_info, est_meta_large

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://www.sxbid.com.cn/f/list-0aba50622c38448a87f83c3104f04b53.html?accordToLaw=0"
# driver=webdriver.Chrome()
# driver.maximize_window()
# driver.get(url)

_name_ = 'shanxi'


def f1(driver, num):

    locator = (By.XPATH, '//div[@class="bidMessage"]//ul[not(@style)]//table[@class="download_table"]/tbody/tr[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath(
        '//div[@class="bidMessage"]//ul[@class="on"]//a[@class="current"] | //div[@class="bidMessage"]//ul[not(@style)]//a[@class="current"]').text.strip()


    if int(cnum) != num:

        val = driver.find_element_by_xpath(
            '//div[@class="bidMessage"]//ul[not(@style)]//table[@class="download_table"]/tbody/tr[1]//a').get_attribute(
            "href").rsplit('/',maxsplit=1)[1]

        driver.execute_script("page_1({},15,'');".format(num))

        locator = (By.XPATH,
                   '//div[@class="bidMessage"]//ul[not(@style)]//table[@class="download_table"]/tbody/tr[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))


    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', class_='download_table').find('tbody')
    trs = div.find_all('tr')
    for tr in trs:
        tds = tr.find_all('td')
        name = tds[1]['title']
        href = tds[1].a['href']
        jy_type = tds[2].get_text()
        ggstart_time = tds[3].get_text()
        diqu = tds[1].span.get_text().strip(']').strip('[') if tds[1].span else None
        if diqu:
            info = {"diqu": diqu, 'jy_type': jy_type}
            info = json.dumps(info, ensure_ascii=False)
        else:
            info = {'jy_type': jy_type}
            info = json.dumps(info, ensure_ascii=False)

        if 'http' in href:
            href = href
        else:
            href = 'http://www.sxbid.com.cn' + href

        tmp = [name, href, ggstart_time, info]
        # print(tmp)
        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df


def f4(driver, num):
    locator = (
    By.XPATH, '//div[@class="bidMessage"]//ul[not(@style)]//table[@class="download_table"]/tbody/tr[1]/td[2]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath(
        '//div[@class="bidMessage"]//ul[@class="on"]//a[@class="current"] | '
        '//div[@class="bidMessage"]//ul[not(@style)]//a[@class="current"]').text.strip()

    if int(cnum) != num:

        val = driver.find_element_by_xpath(
            '//div[@class="bidMessage"]//ul[not(@style)]//table[@class="download_table"]/tbody/tr[1]/td[2]').get_attribute(
            "onclick").rsplit('/',maxsplit=1)[1]
        driver.execute_script("page_1({},15,'');".format(num))

        locator = (By.XPATH,
        '//div[@class="bidMessage"]//ul[not(@style)]//table[@class="download_table"]/tbody/tr[1]/td[2][not(contains(@onclick,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))



    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', class_='download_table').find('tbody')
    trs = div.find_all('tr')
    for tr in trs:
        tds = tr.find_all('td')
        name = tds[1]['title']
        href = tds[1]['onclick']
        href = re.findall('goURL\((.+\.html)', href)[0].strip("'")
        jy_type = tds[2].get_text()
        ggstart_time = tds[3].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.sxbid.com.cn' + href

        info = {'jy_type': jy_type}
        info = json.dumps(info, ensure_ascii=False)

        tmp = [name, href, ggstart_time, info]

        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df


def f2(driver):

    locator = (
    By.XPATH, '//div[@class="bidMessage"]//ul[not(@style)]//table[@class="download_table"]/tbody/tr[1]/td[2]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath(
        '//div[@class="bidMessage"]//ul[not(@style)]/div[@class="pagination"]//span').text
    total = re.findall('共(\d+?)页', page)[0]

    total = int(total)

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//form[@id="loginForm"] | //div[@class="page_main"]')
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    try:
        driver.find_element_by_xpath('//div[@class="page_main"]')
    except:
        driver.find_element_by_xpath('//form[@id="loginForm"]')
        return '登录'

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
    div = soup.find('div', class_="page_main")
    try:
        div.find('p', class_="article_info").extract()
    except:
        pass

    return div


data = [

    ###包含:变更,招标,控制价
    ["dianzi_zhaobiao_gg","http://www.sxbid.com.cn/f/list-3d6e34806adf48d5a59ad94f6f31deb5.html?accordToLaw=1",[ "name", "href",  "ggstart_time","info"],f1,f2],
    ["dianzi_zhongbiaohx_gg","http://www.sxbid.com.cn/f/list-0aba50622c38448a87f83c3104f04b53.html?accordToLaw=1",[ "name", "href",  "ggstart_time","info"],f1,f2],
    ["dianzi_zhongbiao_gg","http://www.sxbid.com.cn/f/list-5579131cdc344620ae11555919316acf.html?accordToLaw=1",[ "name", "href",  "ggstart_time","info"],f1,f2],

    ["dianzi_gqita_biangengzbfs_gg","http://www.sxbid.com.cn/f/list-64a95c1eb7b9448393d668838a6923ee.html?accordToLaw=1",[ "name", "href",  "ggstart_time","info"],add_info(f4,{"gclx":"变更招标方式"}),f2],

    # ###要登录
    ["jqita_zhaobaio_gg","http://www.sxbid.com.cn/f/list-3d6e34806adf48d5a59ad94f6f31deb5.html?accordToLaw=0",[ "name", "href",  "ggstart_time","info"],add_info(f1,{'hreftype':'不可抓网页'}),f2],
    ["jqita_zhongbiaohx_gg","http://www.sxbid.com.cn/f/list-0aba50622c38448a87f83c3104f04b53.html?accordToLaw=0",[ "name", "href",  "ggstart_time","info"],add_info(f1,{'hreftype':'不可抓网页'}),f2],
    ["jqita_zhongbiao_gg","http://www.sxbid.com.cn/f/list-5579131cdc344620ae11555919316acf.html?accordToLaw=0",[ "name", "href",  "ggstart_time","info"],add_info(f1,{'hreftype':'不可抓网页'}),f2],
    ["jqita_gqita_biangengzbfs_gg","http://www.sxbid.com.cn/f/list-64a95c1eb7b9448393d668838a6923ee.html?accordToLaw=0",[ "name", "href",  "ggstart_time","info"],add_info(f4,{"gclx":"变更招标方式",'hreftype':'不可抓网页'}),f2],

    ["feigong_zhaobiao_gg", "http://www.sxbid.com.cn/f/list-f368055b9dd748089851eba6519b205f.html?accordToLaw=0",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {"zbfs": "非公开招标",'hreftype':'不可抓网页'}), f2],
    ["feigong_zhongbiaohx_gg", "http://www.sxbid.com.cn/f/list-44ec6e4a351946b7bf347c057cfde33e.html?accordToLaw=0",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {"zbfs": "非公开招标",'hreftype':'不可抓网页'}), f2],
    ["feigong_zhongbiao_gg", "http://www.sxbid.com.cn/f/list-b18c9f09c5b2476cb08db02884511b9b.html?accordToLaw=0",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {"zbfs": "非公开招标",'hreftype':'不可抓网页'}), f2],

]


##### 注意
##### 部分网页在特定时间段内需要登录,过了此时间就不用登录
##### 需定时将gg_html表中page='登录'的对象删除重新爬取

def work(conp, **args):
    est_meta(conp, data=data, diqu="山西省山西", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "shanxi1", "shanxi"]

    work(conp=conp, num=1, cdc_total=2, headless=False)
