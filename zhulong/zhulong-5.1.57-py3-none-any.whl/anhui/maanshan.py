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

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]
from zhulong.util.conf import get_conp

# url="http://zbcg.mas.gov.cn/maszbw/jygg/028001/028001001/028001001001/MoreInfo.aspx?CategoryNum=028001001001"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)
_name_='maanshan'


def f1(driver,num):

    locator = (By.XPATH, '//td[@class="MiddleBg"]/table//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum=driver.find_element_by_xpath('//div[@id="MoreInfoList1_Pager"]/table//tr//font[@color="red"]/b').text

    if int(cnum) != num:
        val = driver.find_element_by_xpath('//td[@class="MiddleBg"]/table//tr[1]//a').get_attribute('href')[-50:-20]
        driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','{}')".format(num))
        locator = (By.XPATH, '//td[@class="MiddleBg"]/table//tr[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', id='MoreInfoList1_DataGrid1')
    trs = div.find_all('tr', valign='top')

    for tr in trs:
        tds = tr.find_all('td')
        href = tds[1].a['href']
        name = tds[1].a['title']
        ggstart_time = tds[2].get_text().strip()

        if 'http' in href:
            href = href
        else:
            href = 'http://zbcg.mas.gov.cn' + href
        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"] = None


    return df



def f2(driver):
    locator = (By.XPATH, '//td[@class="MiddleBg"]/table//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total_ = driver.find_element_by_xpath(
        '//div[@id="MoreInfoList1_Pager"]/table//tr/td[1]/font[2]/b').text
    total = int(total_)

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//table[@id="tblInfo"] | //div[contains(@id,"menutab") and (not(@style) or @style="")]')

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

    div = soup.find('table', id="tblInfo")
    if div == None:
        div = soup.find('div', attrs={'id': re.compile('menutab_6_\d'), 'style': ''})

    return div


def get_data():
    data = []

    #gcjs
    ggtype1 = OrderedDict([("zhaobiao","001"),("gqita_da_bian", "002"), ("zhongbiaohx", "003"),("gqita","005"),("zhongbiao","006")])
    #zfcg
    ggtype2 = OrderedDict([("zhaobiao","001"),("gqita_da_bian","002"),("gqita_zhong_liu", "003"), ("gqita_zhao_bian_danyilaiyuan", "004")])

    ##zfcg_gcjs
    adtype1 = OrderedDict([('市区','001'),("含山", "002"), ("和县", "003"),("当涂","004")])


    #gcjs
    for w1 in ggtype1.keys():
        for w2 in adtype1.keys():
            href = "http://zbcg.mas.gov.cn/maszbw/jygg/028001/028001{jy}/028001{jy}{dq}/MoreInfo.aspx?CategoryNum=028001{jy}{dq}".format(dq=adtype1[w2],jy=ggtype1[w1])
            tmp = ["gcjs_%s_diqu%s_gg" % (w1, adtype1[w2]), href, ["name","ggstart_time","href",'info'],
                   add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)
    #zfcg
    for w1 in ggtype2.keys():
        for w2 in adtype1.keys():
            href = "http://zbcg.mas.gov.cn/maszbw/jygg/028002/028002{jy}/028002{jy}{dq}/MoreInfo.aspx?CategoryNum=028002{jy}{dq}".format(dq=adtype1[w2],jy=ggtype2[w1])
            tmp = ["zfcg_%s_diqu%s_gg" % (w1, adtype1[w2]), href, ["name","ggstart_time","href",'info'],
                   add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)

    #biaoqian
    for w2 in adtype1.keys():
        href="http://zbcg.mas.gov.cn/maszbw/jygg/028007/028007{dq}/MoreInfo.aspx?CategoryNum=028007{dq}".format(dq=adtype1[w2])
        tmp = ["jqita_yucai_diqu%s_gg" % (adtype1[w2]), href, ["name","ggstart_time","href",'info'],
               add_info(f1, {"diqu": w2}), f2]
        data.append(tmp)

    data1 = data.copy()

    return data1

data=get_data()

# pprint(data)

def work(conp,**args):
    est_meta(conp,data=data,diqu="安徽省马鞍山市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':

    work(conp=["postgres","since2015","192.168.3.171","anhui","maanshan"])
    pass