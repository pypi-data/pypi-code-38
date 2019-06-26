import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write, db_command, db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

import json
from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, est_tbs, add_info

_name_ = "qiannan"


def f1(driver, num):
    locator = (By.XPATH, '//tr[@height="25"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=int(re.findall('Paging=(\d+)',url)[0])


    if cnum != num:
        val = driver.find_element_by_xpath('//tr[@height="25"][1]//a').get_attribute('href')[-40:-10]
        url=re.sub('Paging=\d+','Paging=%s'%num,url)
        driver.get(url)
        locator = (By.XPATH, '//tr[@height="25"][1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    divs = soup.find_all("tr",height="25")

    data = []
    for div in divs:
        name = div.find("a")['title']
        href = div.find("a")['href']
        ggstart_time = div.find("td", align="right").get_text().strip(']').strip('[')
        if 'http' in href:
            href=href
        else:
            href='http://www.qnggzy.cn' + href

        tmp = [name, href, ggstart_time]


        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df

def f2(driver):
    locator = (By.XPATH, '//tr[@height="25"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        total = driver.find_element_by_xpath('//td[@class="huifont"]').text
        total=re.findall('/(\d+)$',total)[0]
    except:
        total = 1
    driver.quit()

    return int(total)




def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="subgundong"][string-length()>100]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

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

    div = soup.find('div', class_='subgundong')

    return div


data = [
    ["gcjs_zhaobiao_gg", "http://www.qnggzy.cn/TPWeb_QN/gcjs/009001/?Paging=1",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_gqita_da_bian_gg", "http://www.qnggzy.cn/TPWeb_QN/gcjs/009008/?Paging=1",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg", "http://www.qnggzy.cn/TPWeb_QN/gcjs/009002/?Paging=1",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_liubiao_gg", "http://www.qnggzy.cn/TPWeb_QN/gcjs/009005/?Paging=1",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://www.qnggzy.cn/TPWeb_QN/zfcg/010001/?Paging=1",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_gqita_da_bian_gg", "http://www.qnggzy.cn/TPWeb_QN/zfcg/010008/?Paging=1",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_biangeng_gg", "http://www.qnggzy.cn/TPWeb_QN/zfcg/010002/?Paging=1",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_zhongbiao_gg", "http://www.qnggzy.cn/TPWeb_QN/zfcg/010003/?Paging=1",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_liubiao_gg", "http://www.qnggzy.cn/TPWeb_QN/zfcg/010005/?Paging=1",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_zhaobiao_danyilaiyuan_gg", "http://www.qnggzy.cn/TPWeb_QN/zfcg/010004/?Paging=1",
     ["name", "href", "ggstart_time", "info"], add_info(f1,{"zbfs":"单一来源"}), f2],

    ["jqita_gqita_diqu1_gg", "http://www.qnggzy.cn/TPWeb_QN/qtjy/013001/?Paging=1",
     ["name", "href", "ggstart_time", "info"], add_info(f1,{"diqu":"福泉市"}), f2],

    ["jqita_gqita_diqu2_gg", "http://www.qnggzy.cn/TPWeb_QN/qtjy/013002/?Paging=1",
     ["name", "href", "ggstart_time", "info"], add_info(f1,{"diqu":"瓮安县"}), f2],

    ["jqita_gqita_diqu3_gg", "http://www.qnggzy.cn/TPWeb_QN/qtjy/013003/?Paging=1",
     ["name", "href", "ggstart_time", "info"], add_info(f1,{"diqu":"贵定县"}), f2],

    ["jqita_gqita_diqu4_gg", "http://www.qnggzy.cn/TPWeb_QN/qtjy/013004/?Paging=1",
     ["name", "href", "ggstart_time", "info"], add_info(f1,{"diqu":"龙里县"}), f2],

    ["jqita_gqita_diqu5_gg", "http://www.qnggzy.cn/TPWeb_QN/qtjy/013005/?Paging=1",
     ["name", "href", "ggstart_time", "info"], add_info(f1,{"diqu":"惠水县"}), f2],
    ["jqita_gqita_diqu6_gg", "http://www.qnggzy.cn/TPWeb_QN/qtjy/013006/?Paging=1",
     ["name", "href", "ggstart_time", "info"], add_info(f1,{"diqu":"长顺县"}), f2],

    ["jqita_gqita_diqu7_gg", "http://www.qnggzy.cn/TPWeb_QN/qtjy/013007/?Paging=1",
     ["name", "href", "ggstart_time", "info"], add_info(f1,{"diqu":"独山县"}), f2],

    ["jqita_gqita_diqu8_gg", "http://www.qnggzy.cn/TPWeb_QN/qtjy/013008/?Paging=1",
     ["name", "href", "ggstart_time", "info"], add_info(f1,{"diqu":"三都县"}), f2],

    ["jqita_gqita_diqu9_gg", "http://www.qnggzy.cn/TPWeb_QN/qtjy/013009/?Paging=1",
     ["name", "href", "ggstart_time", "info"], add_info(f1,{"diqu":"荔波县"}), f2],

    ["jqita_gqita_diqu10_gg", "http://www.qnggzy.cn/TPWeb_QN/qtjy/013010/?Paging=1",
     ["name", "href", "ggstart_time", "info"], add_info(f1,{"diqu":"平塘县"}), f2],

    ["jqita_gqita_diqu11_gg", "http://www.qnggzy.cn/TPWeb_QN/qtjy/013011/?Paging=1",
     ["name", "href", "ggstart_time", "info"], add_info(f1,{"diqu":"罗甸县"}), f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="贵州省黔南州", **args)

    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guizhou", "qiannan"], pageloadstrategy='none',num=1,total=2)