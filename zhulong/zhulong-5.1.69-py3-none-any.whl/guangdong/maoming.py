import json

from collections import OrderedDict
from pprint import pprint

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
from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, add_info, est_gg

# driver=webdriver.Chrome()
# url="http://www.bygzjy.cn/f/trade/annogoods/list?selectedProjectType=3"
# driver.get(url)

_name_ = 'maoming'


def f1(driver, num):
    locator = (By.XPATH, '//tr[@height="22"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url = driver.current_url
    cnum = int(re.findall(r'Paging=(\d+)', url)[0])

    if cnum != num:
        page_count=len(driver.page_source)
        val = driver.find_element_by_xpath(
            '//tr[@height="22"][1]//a').get_attribute('href')[-40:-10]

        url=re.sub('Paging=\d+','Paging=%s'%num,url)

        driver.get(url)

        locator = (
            By.XPATH, "//tr[@height='22'][1]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(
            driver, 10).until(
            EC.presence_of_element_located(locator))
        WebDriverWait(
            driver, 10).until(
            lambda driver:len(driver.page_source)!=page_count)

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')

    dls = soup.find_all("tr",height='22')
    data = []
    for dl in dls:

        name = dl.find('a')['title']
        href = dl.find('a')['href']
        ggstart_time = dl.find('td', width="100").get_text().strip()

        if 'http' in href:
            href = href
        else:
            href = 'http://zffw.gdmm.com' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None

    return df


def f2(driver):
    locator = (By.XPATH, '//tr[@height="22"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total=driver.find_element_by_xpath('//font[@color="blue"][2]/b').text

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)
    try:
        locator = (
            By.XPATH,
            '//table[@id="Table1"][string-length()>50] | //table[@id="tblInfo"][string-length()>50]')
        WebDriverWait(
            driver, 20).until(
            EC.presence_of_all_elements_located(locator))

    except:
        if '404' in driver.title:
            return 404
        else:
            raise TimeoutError


    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 5:
            break

    # f3 情况1
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('table', id='Table1')
    if not div:
        div=soup.find('table',id='tblInfo')
    # print(driver.title)
    return div


def get_data():
    data = []

    # gcjs
    ggtype1 = OrderedDict([("zhaobiao", "001"), ("biangeng", "002"),
                           ("zhongbiaohx", "003"), ("liubiao", "004")])

    gctype1 = OrderedDict([("shigong", "001,施工"), ("kancha",
                                                   "002,勘察设计"), ("jianli", "003,监理"), ("qita", "004,其他")])

    zbtype1 = OrderedDict([("gongkai", "001,公开招标"), ("yaoqing", "002,邀请招标"), ("tanpan", "003,竞争性谈判"),
                           ("xunjia", "004,询价"), ("danyilaiyuan", "005,单一来源"), ("cuoshang", "003,竞争性磋商")])

    adtype1 = OrderedDict([('市直', '001'), ("区县", "002")])

    # gcjs
    for w1 in ggtype1.keys():
        for w2 in adtype1.keys():
            for w3 in gctype1.keys():
                href = "http://zffw.gdmm.com/mmzbtb/jyxx/033001/033001{dq}/033001{dq}{jy}/033001{dq}{jy}{gc}/?Paging=1".format(
                    dq=adtype1[w2], jy=ggtype1[w1], gc=gctype1[w3].split(',')[0])
                tmp = ["gcjs_%s_%s_diqu%s_gg" % (w1, w3, adtype1[w2]), href, ["name", "ggstart_time", "href", 'info'],
                       add_info(f1, {"diqu": w2, 'gclx': gctype1[w3].split(',')[1]}), f2]
                data.append(tmp)

    # zfcg
    for w1 in ggtype1.keys():
        for w2 in adtype1.keys():
            for w3 in zbtype1.keys():
                href = "http://zffw.gdmm.com/mmzbtb/jyxx/033002/033002{dq}/033002{dq}{jy}/033002{dq}{jy}{gc}/?Paging=1".format(
                    dq=adtype1[w2], jy=ggtype1[w1], gc=zbtype1[w3].split(',')[0])
                tmp = ["zfcg_%s_%s_diqu%s_gg" % (w1, w3, adtype1[w2]), href,
                       ["name", "ggstart_time", "href", 'info'],
                       add_info(f1, {"diqu": w2, 'zfcg': zbtype1[w3].split(',')[1]}), f2]
                data.append(tmp)

    data1 = data.copy()

    return data1


data = get_data()


def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省茂名市", **args)
    est_html(conp, f=f3,pageLoadStrategy='none',pageloadtimeout=80, **args)


if __name__ == "__main__":

    work(
        conp=[
            "postgres",
            "since2015",
            '192.168.3.171',
            "guangdong",
            "maoming_test"],
        )
    pass
