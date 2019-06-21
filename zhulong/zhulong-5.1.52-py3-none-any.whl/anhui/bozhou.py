import time
from collections import OrderedDict
from os.path import dirname, join
from pprint import pprint

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json

from zhulong.util.etl import est_tbs, est_meta, est_html, gg_existed, add_info

from zhulong.util.conf import get_conp

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url="http://www.bzztb.gov.cn/BZWZ/jyxx/003001/003001001/003001001001/003001001001001/"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)
#

_name_='bozhou'


def f1(driver,num):


    locator = (By.XPATH,'(//table[@id="MoreInfoList1_moreinfo"]//tr[@height="30px"])[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=driver.find_element_by_xpath('//td[@class="yahei redfont"]').text
    if int(cnum) != num:
        val=driver.find_element_by_xpath('(//table[@id="MoreInfoList1_moreinfo"]//tr[@height="30px"])[1]//a').get_attribute('href')[-50:-25]
        url=re.sub('Paging=\d+','Paging=%d'%num,url)
        driver.get(url)
        locator=(By.XPATH,'(//table[@id="MoreInfoList1_moreinfo"]//tr[@height="30px"])[1]//a[not(contains(@href,"%s"))]'%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('td', align="right")
    tbody = div.find('tbody')
    trs = tbody.find_all('tr', height='30px', recursive=False)

    for tr in trs:
        table = tr.find('table')
        tds = table.find_all('td')
        href = tds[-2].a['href']
        name = tds[-2].a['title'].strip()
        ggstart_time = tds[-1].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://ggzy.bozhou.gov.cn' + href

        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"] = None
    return df



def f2(driver):
    locator = (By.XPATH, '(//table[@id="MoreInfoList1_moreinfo"]//tr[@height="30px"])[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total=driver.find_element_by_xpath('//td[@class="huifont"]').text
    total=re.findall('/(\d+)',total)[0]
    total = int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)


    locator = (By.XPATH, '//table[@id="tblInfo"][string-length()>10]')

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
    div = soup.find('table',id='tblInfo')
    return div





def get_data():
    data = []

    # zfcg
    ggtype1 = OrderedDict([("zhaobiao", "001"), ("zhongbiao", "002"), ("gqita_da_bian", "003")])
    # gcjs
    ggtype2 = OrderedDict([("zhaobiao", "001"), ("zhongbiaohx", "002"), ("gqita_da_bian", "003"), ("zhongbiao", "004")])


    ##gcjs_zfcg
    adtype1 = OrderedDict([('市中心', '001,0'), ("涡阳县", "002,3"), ("蒙城县", "003,4"), ("利辛县", "004,5")])

    adtype2=OrderedDict([('市本级','001,1'),('谯城区','002,2')])

    #gcjs

    for w1 in ggtype2.keys():
        for w2 in adtype1.keys():
            if w2 == '市中心':
                for w3 in adtype2.keys():

                    href='http://ggzy.bozhou.gov.cn/BZWZ/jyxx/003001/003001{jy}/003001{jy}{dq}/003001{jy}{dq}{dq2}/moreinfo.aspx?Paging=1'.format(
                    dq=adtype1[w2].split(',')[0], jy=ggtype2[w1],dq2=adtype2[w3].split(',')[0])
                    tmp = ["gcjs_{0}_diqu{1}_gg".format(w1, adtype2[w3].split(',')[1]), href, ["name", "ggstart_time", "href", 'info'],
                           add_info(f1, {"diqu": w3}), f2]
                    data.append(tmp)
            else:
                href = "http://ggzy.bozhou.gov.cn/BZWZ/jyxx/003001/003001{jy}/003001{jy}{dq}/moreinfo.aspx?Paging=1".format(
                    dq=adtype1[w2].split(',')[0], jy=ggtype2[w1])
                tmp = ["gcjs_{0}_diqu{1}_gg" .format(w1, adtype1[w2].split(',')[1]), href, ["name", "ggstart_time", "href", 'info'],
                   add_info(f1, {"diqu": w2}), f2]
                data.append(tmp)

    #zfcg
    for w1 in ggtype1.keys():
        for w2 in adtype1.keys():
            if w2 == '市中心':
                for w3 in adtype2.keys():
                    href = 'http://ggzy.bozhou.gov.cn/BZWZ/jyxx/003002/003002{jy}/003002{jy}{dq}/003002{jy}{dq}{dq2}/moreinfo.aspx?Paging=1'.format(
                        dq=adtype1[w2].split(',')[0], jy=ggtype1[w1], dq2=adtype2[w3].split(',')[0])
                    tmp = ["zfcg_{0}_diqu{1}_gg".format(w1, adtype2[w3].split(',')[1]), href,
                           ["name", "ggstart_time", "href", 'info'],
                           add_info(f1, {"diqu": w3}), f2]
                    data.append(tmp)
            else:
                href = "http://ggzy.bozhou.gov.cn/BZWZ/jyxx/003002/003002{jy}/003002{jy}{dq}/moreinfo.aspx?Paging=1".format(
                    dq=adtype1[w2].split(',')[0], jy=ggtype1[w1])
                tmp = ["zfcg_{0}_diqu{1}_gg".format(w1, adtype1[w2].split(',')[1]), href,
                       ["name", "ggstart_time", "href", 'info'],
                       add_info(f1, {"diqu": w2}), f2]
                data.append(tmp)


    # remove_arr = [""]
    data1 = data.copy()
    # for w in data:
    #     if w[0] in remove_arr: data1.remove(w)


    return data1


data = get_data()
# pprint(data)


##网站域名变更 http://ggzy.bozhou.gov.cn
##变更时间 2019-5-19


def work(conp,**args):
    est_meta(conp=conp,data=data,diqu="安徽省亳州市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':


    # work(conp=["postgres", "since2015", "192.168.3.171", "anhui", "bozhou"],cdc_total=None,num=1,headless=False,total=2)
    pass
