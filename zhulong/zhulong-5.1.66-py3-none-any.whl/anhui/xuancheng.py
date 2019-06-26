import time
from collections import OrderedDict
from os.path import dirname, join

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

from zhulong.util.etl import est_tbs, est_meta, est_html, gg_existed, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]


# url="http://ggzyjy.xuancheng.gov.cn/XCTPFront/zfcg/012001/012001001/"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_ = 'xuancheng'


def f1(driver, num):

    locator = (By.XPATH, '//tr[@class="trfont"][1]/td[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url=driver.current_url
    main_url=url.rsplit('=',maxsplit=1)[0]
    cnum=url.rsplit('=',maxsplit=1)[1]

    if int(cnum) != num:
        val = driver.find_element_by_xpath('//tr[@class="trfont"][1]/td[2]/a').get_attribute(
            "href")[- 30:-5]
        url=main_url+'=%s'%num
        driver.get(url)

        locator = (By.XPATH, '//tr[@class="trfont"][1]/td[2]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data_ = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find_all('tr', class_="trfont")

    for tr in trs:
        href = tr.find('td', align='left').a['href']
        name = tr.find('td', align='left').a['title']

        ggstart_time = tr.find('td', align='right').get_text()
        if 'http' in href:
            href = href
        else:
            href = 'http://ggzyjy.xuancheng.gov.cn' + href

        tmp = [name, ggstart_time, href]

        data_.append(tmp)
    df = pd.DataFrame(data=data_)
    df["info"] = None
    return df


def f2(driver):

    locator = (By.XPATH, '//tr[@class="trfont"][1]/td[2]/a')

    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('//td[@class="huifont"]').text
    total_ = re.findall(r'/(\d+)', page)[0]

    total = int(total_)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[contains(@id,"menutab") and (not(@style) or @style="")] | //div[@class="ewb-main"]')

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

    div = soup.find('div', id="mainContent")
    if div == None:
        div = soup.find('div', attrs={'id': re.compile('menutab_6_\d'), 'style': ''})
    return div

def get_data():
    data = []

    ##gcjs
    ggtype1 = OrderedDict([("zhaobiao", "001"), ("gqita_da_bian","002"),("zhongbiaohx", "003"), ("zhongbiao", "004")])
    ##zfcg
    ggtype2 = OrderedDict([("zhaobiao", "001"), ("yucai", "002"),("gqita_da_bian","003"), ("zhongbiao", "004")])
    ##shehuicaigou
    ggtype3 = OrderedDict([("zhaobiao", "001"), ("biangeng", "002"),("gqita_da_bian","003"), ("zhongbiao", "004")])
    adtype1 = OrderedDict([('本级','1'),("宣州", "2"), ("郎溪", "3"), ("广德", "4"), ("宁国", "5"),
                          ('泾县','6'),('绩溪','7'),('旌德','8')])

    ##gcjs
    for w1 in ggtype1.keys():
        for w2 in adtype1.keys():
            href="http://ggzyjy.xuancheng.gov.cn/XCTPFront/jsgc/01100{0}/01100{1}{2}/?Paging=1".format(adtype1[w2],adtype1[w2],ggtype1[w1])
            tmp=["gcjs_%s_diqu%s_gg"%(w1,adtype1[w2]),href,["name","ggstart_time","href",'info'],add_info(f1,{"diqu":w2}),f2]
            data.append(tmp)

    ##zfcg
    for w1 in ggtype2.keys():
        for w2 in adtype1.keys():
            href="http://ggzyjy.xuancheng.gov.cn/XCTPFront/zfcg/01200{0}/01200{1}{2}/?Paging=1".format(adtype1[w2],adtype1[w2],ggtype2[w1])
            tmp=["zfcg_%s_diqu%s_gg"%(w1,adtype1[w2]),href,["name","ggstart_time","href",'info'],add_info(f1,{"diqu":w2}),f2]
            data.append(tmp)

    ##shehuicaigou
    for w1 in ggtype3.keys():
        for w2 in adtype1.keys():
            href="http://ggzyjy.xuancheng.gov.cn/XCTPFront/xaxm/02200{0}/02200{1}{2}/?Paging=1".format(adtype1[w2],adtype1[w2],ggtype3[w1])
            tmp=["qsy_%s_diqu%s_gg"%(w1,adtype1[w2]),href,["name","ggstart_time","href",'info'],add_info(f1,{"diqu":w2,"gclx":"限额以下项目"}),f2]
            data.append(tmp)


    data1 = data.copy()


    return data1

data = get_data()





def work(conp, **args):
    est_meta(conp, data=data, diqu="安徽省宣城市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anhui", "xuancheng"])

    pass

