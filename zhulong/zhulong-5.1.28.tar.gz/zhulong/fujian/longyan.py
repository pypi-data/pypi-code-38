from collections import OrderedDict
from os.path import dirname, join

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_command,db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

import json
from zhulong.util.etl import add_info, est_meta, est_html, est_tbs, gg_existed
from zhulong.util.conf import get_conp

_name_="longyan"



def f1(driver, num):
    url = driver.current_url
    locator = (By.XPATH, "//ul[@class='list']/li[1]/a")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-30:]
    try:
        locator = (By.XPATH, "//a[@class='wb-page-default wb-page-number wb-page-family']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        cnum = re.findall(r'(\d+)/', str)[0]
    except:
        cnum = 1
    if num != int(cnum):
        driver.execute_script("ShowAjaxNewPage(window.location.pathname,'categorypagingcontent',{})".format(num))
        locator = (By.XPATH, "//ul[@class='list']/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("ul", class_="list")
    trs = table.find_all("li", class_="list-item clearfix")
    data = []
    for tr in trs:
        a = tr.find('a')
        try:
            title = a["title"].strip()
        except:
            title = a.text.strip()

        href = a["href"]
        if ('http' in href) or ('https' in href):
            link = href
        else:
            link = "https://www.lyggzy.com.cn" + href.strip()
        td = tr.find("span", class_='list-date').text.strip()
        if '[' in title:
            ts = re.findall(r'^\[(.*?)\]', title)[0]
        else:
            ts = ''
        info = json.dumps({'leixing':ts}, ensure_ascii=False)
        tmp = [title, td, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df



def f2(driver):
    url = driver.current_url
    if '本栏目暂无信息' in driver.page_source:
        return 0
    locator = (By.XPATH, "//ul[@class='list']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//a[@class='wb-page-default wb-page-number wb-page-family']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = re.findall(r'/(\d+)', st)[0]
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    if '404' in driver.title:
        return 404

    locator = (By.XPATH, "//div[@class='detail-content'][string-length()>30]")
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
    div = soup.find('div', class_="detail-content")
    return div


def get_data():
    data = []
    # 工程建设部分
    xs = OrderedDict([("新罗", "001"),("长汀", "002"), ("永定", "003"), ("上杭", "004"), ("武平", "005"),
                      ("连城", "006"), ("漳平", "007")])
    ggtype = OrderedDict([("zhaobiao", "001"),("gqita_bian_da", "003"),("zhongbiao", "004")])

    for w1 in xs.keys():
        for w2 in ggtype.keys():
            p1 = "081008%s" % (xs[w1])
            p2 = "081008%s%s" % (xs[w1], ggtype[w2])
            href = "https://www.lyggzy.com.cn/lyztb/gcjs/081008/%s/%s/" % (p1, p2)

            tb = "gcjs_%s_diqu%s_gg" % (w2, xs[w1])
            col = ["name", "ggstart_time", "href", "info"]
            tmp = [tb, href, col, add_info(f1, {"diqu": w1}), f2]
            data.append(tmp)

    data1 = data.copy()
    remove_arr = []
    for w in data:
        if w[0] in remove_arr: data1.remove(w)
    return data1
    # 创建data

data1 = get_data()



data2 = [
    ["gcjs_zhaobiao_yifajinchang_gg",
     "https://www.lyggzy.com.cn/lyztb/gcjs/081001/081001003/081001003001/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhaobiao_qita_gg",
     "https://www.lyggzy.com.cn/lyztb/gcjs/081001/081001003/081001003002/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zgysjg_gg",
     "https://www.lyggzy.com.cn/lyztb/gcjs/081001/081001009/",
     ["name", "ggstart_time", "href", "info"],f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "https://www.lyggzy.com.cn/lyztb/gcjs/081001/081001010/",
     ["name", "ggstart_time", "href", "info"],f1, f2],

    ["gcjs_zhongbiao_gg",
     "https://www.lyggzy.com.cn/lyztb/gcjs/081001/081001005/",
     ["name", "ggstart_time", "href", "info"],f1, f2],

    ["zfcg_yucai_gg",
     "https://www.lyggzy.com.cn/lyztb/zfcg/082003/082003007/",
    ["name", "ggstart_time", "href", "info"],f1, f2],

    ["zfcg_gqita_zhao_bian_gg",
     "https://www.lyggzy.com.cn/lyztb/zfcg/082003/082003001/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "https://www.lyggzy.com.cn/lyztb/zfcg/082003/082003002/",
     ["name", "ggstart_time", "href", "info"],f1, f2],

    ["zfcg_yucai_qita_gg",
     "https://www.lyggzy.com.cn/lyztb/zfcg/082001/082001001/",
     ["name", "ggstart_time", "href", "info"],f1, f2],

    ["zfcg_gqita_zhao_bian_qita_gg",
     "https://www.lyggzy.com.cn/lyztb/zfcg/082001/082001002/",
     ["name", "ggstart_time", "href", "info"],f1, f2],

    ["zfcg_zhongbiao_qita_gg",
     "https://www.lyggzy.com.cn/lyztb/zfcg/082001/082001003/",
     ["name", "ggstart_time", "href", "info"],f1, f2],
]

data = data1 + data2

def work(conp,**args):
    est_meta(conp,data=data,diqu="福建省龙岩市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.4.175","fujian","longyan"])

