import time
from collections import OrderedDict
from os.path import join, dirname
from pprint import pprint

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
from zhulong.util.conf import get_conp

# url="http://www.hbzbcg.cn/hbweb/jyxx/002001/002001001/002001001001/MoreInfo.aspx?CategoryNum=002001001001"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_ = 'fuyang'


def f1(driver, num):

    locator = (By.XPATH, '//li[@class="wb-data-list"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=re.findall('Paging=(\d+)',url)[0]
    if int(cnum) != num:
        val=driver.find_element_by_xpath('//li[@class="wb-data-list"][1]//a').get_attribute('href')[-50:-30]
        url=re.sub('Paging=\d+','Paging=%d'%num,url)
        driver.get(url)
        locator=(By.XPATH,'//li[@class="wb-data-list"][1]//a[not(contains(@href,"%s"))]'%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lis = soup.find_all('li', class_='wb-data-list')

    for tr in lis:
        href = tr.div.a['href']
        name = tr.div.a['title']
        ggstart_time = tr.span.get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://jyzx.fy.gov.cn' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//li[@class="wb-data-list"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total=driver.find_element_by_xpath('//td[@class="huifont"]').text
    total=re.findall('/(\d+)',total)[0]

    driver.quit()

    return int(total)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '/html/body')
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    html = driver.page_source
    if '系统出现了错误' in html:
        return '404'
    locator = (By.XPATH, '//div[contains(@id,"menutab") and (not(@style) or @style="")] | //div[@id="mainContent"]')

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
    div = soup.find('div', id='mainContent')
    if div == None:
        div = soup.find('div', attrs={'id': re.compile('menutab_6_\d'), 'style': ''})

    return div



def get_data():
    data = []

    # zfcg
    ggtype1 = OrderedDict([("zhaobiao", "001"), ("gqita_zhong_liu", "002"), ("biangeng", "004"), ("gqita_da_bian", "005"),
                           ('zhaobiao_danyilaiyuan', '007'),('gqita_jinkou','008')])
    # gcjs_jiaotong_shuili
    ggtype2 = OrderedDict([("zhaobiao", "001"), ("gqita_zhong_liu", "002"), ("biangeng", "003"), ("gqita_da_bian", "004"),('zhongbiaohx','006')])

    #fenshan
    ggtype3 = OrderedDict([("zhaobiao", "001"), ("gqita_zhong_liu", "002"), ("biangeng", "003"), ("gqita_da_bian", "004")])



    ##zfcg_fenshan
    adtype1 = OrderedDict([('市中心', '001'), ("界首市", "002"), ("太和县", "003"), ("临泉县", "004"), ("阜南县", "005"),
                           ('颍上县', '006'), ("颍州区", "007"), ("颍泉及阜合园区", "008"), ("颍东及开发区", "009")])

    #gcjs_jiaotong_shuili
    adtype2 = OrderedDict([('市中心', '001'), ("界首市", "002"), ("太和县", "003"), ("临泉县", "004"), ("阜南县", "005"),
                           ('颍上县', '006')])



    #gcjs
    for w1 in ggtype2.keys():
        for w2 in adtype2.keys():
            href = "http://jyzx.fy.gov.cn/FuYang/jsgc/012{jy}/012{jy}{dq}/?Paging=1".format(
                dq=adtype2[w2], jy=ggtype2[w1])
            tmp = ["gcjs_{0}_diqu{1}_gg" .format(w1, adtype2[w2]), href, ["name", "ggstart_time", "href", 'info'],
                   add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)
    ##jiaotong
    for w1 in ggtype2.keys():
        for w2 in adtype2.keys():
            href = "http://jyzx.fy.gov.cn/FuYang/jtys/013{jy}/013{jy}{dq}/?Paging=1".format(
                dq=adtype2[w2], jy=ggtype2[w1])
            tmp = ["gcjs_jiaotong_{0}_diqu{1}_gg" .format(w1, adtype2[w2]), href, ["name", "ggstart_time", "href", 'info'],
                   add_info(f1, {"diqu": w2,"gclx":"交通工程"}), f2]
            data.append(tmp)
    ##shuili
    for w1 in ggtype2.keys():
        for w2 in adtype2.keys():
            href = "http://jyzx.fy.gov.cn/FuYang/slgc/014{jy}/014{jy}{dq}/?Paging=1".format(
                dq=adtype2[w2], jy=ggtype2[w1])
            tmp = ["gcjs_shuili_{0}_diqu{1}_gg" .format(w1, adtype2[w2]), href, ["name", "ggstart_time", "href", 'info'],
                   add_info(f1, {"diqu": w2,"gclx":"水利工程"}), f2]
            data.append(tmp)

    #zfcg
    for w1 in ggtype1.keys():
        for w2 in adtype1.keys():
            href = "http://jyzx.fy.gov.cn/FuYang/zfcg/011{jy}/011{jy}{dq}/?Paging=1".format(
                dq=adtype1[w2], jy=ggtype1[w1])

            if 'jinkou' in w1:
                tmp = ["zfcg_%s_diqu%s_gg" % (w1, adtype1[w2]), href, ["name", "ggstart_time", "href", 'info'],
                       add_info(f1, {"diqu": w2,"zbfs":"进口商品"}), f2]
            elif 'danyilaiyuan' in w1:
                tmp = ["zfcg_%s_diqu%s_gg" % (w1, adtype1[w2]), href, ["name", "ggstart_time", "href", 'info'],
                       add_info(f1, {"diqu": w2, "zbfs": "单一来源"}), f2]
            else:
                tmp = ["zfcg_%s_diqu%s_gg" % (w1, adtype1[w2]), href, ["name", "ggstart_time", "href", 'info'],
                       add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)
    #fenshan
    for w1 in ggtype3.keys():
        for w2 in adtype1.keys():
            href = "http://jyzx.fy.gov.cn/FuYang/shfw/017{jy}/017{jy}{dq}/?Paging=1".format(
                dq=adtype1[w2], jy=ggtype3[w1])
            tmp = ["qsy_%s_diqu%s_gg" % (w1, adtype1[w2]), href, ["name", "ggstart_time", "href", 'info'],
                   add_info(f1, {"diqu": w2,"gclx":"分散采购"}), f2]
            data.append(tmp)

    # remove_arr = [""]
    data1 = data.copy()
    # for w in data:
    #     if w[0] in remove_arr: data1.remove(w)


    return data1


data = get_data()
# pprint(data)




def work(conp, **args):
    est_meta(conp, data=data, diqu="安徽省阜阳市", **args)
    est_html(conp, f=f3, **args)



if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anhui", "fuyang"],cdc_total=2)
    pass