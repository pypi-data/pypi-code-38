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

from zhulong.util.etl import est_tbs, est_meta, est_html, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url="http://www.bzztb.gov.cn/BZWZ/jyxx/003001/003001001/003001001001/003001001001001/"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)
#

_name_ = 'heilongjiang'


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="right_box"]/ul/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('pageNo=(\d+)&', url)[0]

    if cnum != str(num):
        url = re.sub('pageNo=(\d+)&', 'pageNo=' + str(num) + '&', url)
        val = driver.find_element_by_xpath('//div[@class="right_box"]/ul/li[1]/a').get_attribute('href')[-40:-15]
        driver.get(url)
        locator = (By.XPATH, '//div[@class="right_box"]/ul/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='right_box')
    ul = div.find('ul')
    lis = ul.find_all('li')
    for li in lis:
        href = li.a['href']
        name = li.a.get_text().strip()
        ggstart_time = li.find('span', class_='date').get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.hljggzyjyw.gov.cn' + href

        diqu = re.findall('^\[(.*?)\]', name)
        if diqu:
            info = {"tag": diqu[0]}
            info = json.dumps(info, ensure_ascii=False)
        else:
            info = None

        tmp = [name, ggstart_time, href, info]

        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="right_box"]/ul/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.find_element_by_xpath('//div[@class="page"]/span[2]/b[2]').text

    total = int(page)
    driver.quit()

    return total


def f4(driver, num):
    locator = (By.XPATH, '//div[@class="yahoo"]/div[1]/span/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath('//div[@class="yahoo2"]/div/span/b[2]').text.strip()
    cnum = re.findall('(\d+)/', cnum)[0]
    if int(cnum) != num:
        val = driver.find_element_by_xpath('//div[@class="yahoo"]/div[1]/span/a').get_attribute('onclick')[-40:-15]
        driver.execute_script("javascript:jump('{}');return false;".format(num))
        locator = (By.XPATH, '//div[@class="yahoo"]/div[1]/span/a[not(contains(@onclick,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='yahoo')
    divs = div.find_all('div', class_="xxei")

    for li in divs:
        href = li.find('span', class_="lbej").a['onclick']
        name = li.find('span', class_="lbej").a.get_text()
        ggstart_time = li.find('span', class_="sjej").get_text()
        address = li.find('span', class_="nrej").get_text()
        href = re.findall('javascript:location.href=(.+);return false', href)[0].strip("'")

        if 'http' in href:
            href = href
        else:
            href = 'http://www.hljcg.gov.cn' + href

        info = {'tag': address}
        info = json.dumps(info, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df


def f5(driver):
    locator = (By.XPATH, '//div[@class="yahoo"]/div[1]/span/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.find_element_by_xpath('//div[@class="yahoo2"]/div/span/b[2]').text

    page = re.findall('/(\d+)', page)[0]
    total = int(page)
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@id="contentdiv"][string-length()>10] | //div[@class="xxej"][string-length()>10]')

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

    div = soup.find('div', id='contentdiv')
    if div == None:
        div = soup.find('div', class_='xxej')
        if div == None:
            raise ValueError

    return div


data = [
    ["gcjs_zhaobiao_gg", "http://www.hljggzyjyw.gov.cn/trade/tradezfcg?cid=16&pageNo=1&type=1&notice_name=", ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["gcjs_liubiao_gg", "http://www.hljggzyjyw.gov.cn/trade/tradezfcg?cid=16&pageNo=1&type=5&notice_name=", ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://www.hljggzyjyw.gov.cn/trade/tradezfcg?cid=16&pageNo=1&type=4&notice_name=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg", "http://www.hljggzyjyw.gov.cn/trade/tradezfcg?cid=16&pageNo=1&type=3&notice_name=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ###包含招标，变更
    # ["zfcg_zhaobiao_gg","http://www.hljcg.gov.cn/xwzs!queryXwxxqx.action?lbbh=4",["name","ggstart_time","href","info"],f4,f5],
    # ["zfcg_yucai_gg","http://www.hljcg.gov.cn/xwzs!queryXwxxqx.action?lbbh=99",["name","ggstart_time","href","info"],f4,f5],
    # ["zfcg_zhaobiao_danyilaiyuan_gg","http://www.hljcg.gov.cn/xwzs!queryXwxxqx.action?lbbh=98",["name","ggstart_time","href","info"],add_info(f4,{"zbfs":"单一来源"}),f5],
    # ##包含流标，变更
    # ["zfcg_gqita_liu_bian_gg","http://www.hljcg.gov.cn/xwzs!queryXwxxqx.action?lbbh=30",["name","ggstart_time","href","info"],f4,f5],
    # ["zfcg_zhongbiao_gg","http://www.hljcg.gov.cn/xwzs!queryXwxxqx.action?lbbh=5",["name","ggstart_time","href","info"],f4,f5],

    ["yiliao_zhaobiao_gg", "http://www.hljggzyjyw.gov.cn/trade/tradezfcg?cid=20&pageNo=1&type=1&notice_name=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ##无信息
    ["yiliao_liubiao_gg", "http://www.hljggzyjyw.gov.cn/trade/tradezfcg?cid=20&pageNo=1&type=5&notice_name=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ##只有一条数据
    ["yiliao_zhongbiao_gg", "http://www.hljggzyjyw.gov.cn/trade/tradezfcg?cid=20&pageNo=1&type=4&notice_name=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["yiliao_zhongbiaohx_gg", "http://www.hljggzyjyw.gov.cn/trade/tradezfcg?cid=20&pageNo=1&type=3&notice_name=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="黑龙江省黑龙江市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "heilongjiang", "heilongjiang"]
    # conp = ["postgres", "since2015", "192.168.3.171", "test", "lch"]
    work(conp=conp, num=1, headless=False)