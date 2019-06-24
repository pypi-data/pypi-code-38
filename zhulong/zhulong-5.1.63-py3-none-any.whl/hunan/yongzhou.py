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
from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, add_info

_name_ = 'yongzhou'


# driver=webdriver.Chrome()

# url="""http://ggzy.yzcity.gov.cn/yzweb/jyxx/004001/004001001/004001001001/?Paging=1"""

# driver.get(url)


def f1(driver, num):
    locator = (By.CLASS_NAME, "moreinfo")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url

    url = re.sub("Paging=[0-9]*", "Paging=%d" % num, url)
    driver.get(url)
    locator = (By.CLASS_NAME, "moreinfo")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source

    soup = BeautifulSoup(page, "html.parser")
    td = soup.find("td", class_="moreinfo")
    trs = td.find_all("tr", height="21")
    data = []
    for tr in trs:
        a = tr.find("a")
        td = tr.find_all("td")[-2]
        tmp = [a["title"], "http://ggzy.yzcity.gov.cn" + a["href"], td.text.strip()]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.CLASS_NAME, "moreinfo")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    txt = driver.find_element_by_id("Paging").text
    total = int(re.findall("总页数：([0-9]{1,})", txt)[0])
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.ID, "Table4")

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

    div = soup.find('table', id='Table4')
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


def add_info(f, info):
    def wrap(*krg):
        driver = krg[0]
        if f == f1:
            df = f(*krg)
            a = json.dumps(info, ensure_ascii=False)
            df["info"] = a
            return df
        else:
            return f(*krg)

    return wrap


data = [

    ["gcjs_zhaobiao_sigong_gg", "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004001/004001001/004001001001/?Paging=1",
     ["name", "href", "ggstart_time", "info"]
        , add_info(f1, {"ggtype": "招标公告", "gctype": "施工"}), f2],

    ["gcjs_zhaobiao_jianli_gg", "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004001/004001001/004001001001/?Paging=1",
     ["name", "href", "ggstart_time", "info"]
        , add_info(f1, {"ggtype": "招标公告", "gctype": "监理"}), f2],

    ["gcjs_zhaobiao_kancha_gg", "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004001/004001001/004001001003/?Paging=1",
     ["name", "href", "ggstart_time", "info"]
        , add_info(f1, {"ggtype": "招标公告", "gctype": "勘察设计"}), f2],

    ["gcjs_zhaobiao_quxian_gg", "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004001/004001001/004001001004/?Paging=1",
     ["name", "href", "ggstart_time", "info"]
        , add_info(f1, {"ggtype": "招标公告", "diqu": "区县信息"}), f2],

    ###工程建设-中标
    ["gcjs_zhongbiaohx_sigong_gg", "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004001/004001004/004001004001/?Paging=1",
     ["name", "href", "ggstart_time", "info"]
        , add_info(f1, {"ggtype": "中标候选公告", "gctype": "施工"}), f2],

    ["gcjs_zhongbiaohx_jianli_gg", "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004001/004001004/004001004002/?Paging=1",
     ["name", "href", "ggstart_time", "info"]
        , add_info(f1, {"ggtype": "中标候选公告", "gctype": "监理"}), f2],

    ["gcsj_zhongbiaohx_kancha_gg", "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004001/004001004/004001004003/?Paging=1",
     ["name", "href", "ggstart_time", "info"]
        , add_info(f1, {"ggtype": "中标候选公告", "gctype": "勘察设计"}), f2],

    ["gcsj_zhongbiaohx_quxian_gg", "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004001/004001004/004001004004/?Paging=1",
     ["name", "href", "ggstart_time", "info"]
        , add_info(f1, {"ggtype": "中标候选公告", "diqu": "区县信息"}), f2],

    ###工程建设-变更
    ["gcsj_biangeng_sigong_gg", "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004001/004001002/004001002001/?Paging=1",
     ["name", "href", "ggstart_time", "info"]
        , add_info(f1, {"ggtype": "变更公告", "gctype": "施工"}), f2],

    ["gcsj_biangeng_jianli_gg", "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004001/004001002/004001002002/?Paging=1",
     ["name", "href", "ggstart_time", "info"]
        , add_info(f1, {"ggtype": "变更公告", "gctype": "监理"}), f2],

    ["gcsj_biangeng_kancha_gg", "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004001/004001002/004001002003/?Paging=1",
     ["name", "href", "ggstart_time", "info"]
        , add_info(f1, {"ggtype": "变更公告", "gctype": "勘察设计"}), f2],

    ["gcsj_biangeng_quxian_gg", "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004001/004001002/004001002004/?Paging=1",
     ["name", "href", "ggstart_time", "info"]
        , add_info(f1, {"ggtype": "变更公告", "diqu": "区县信息"}), f2],

    ###政府采购-招标
    ["zfcg_zhaobiao_gc_gg", "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004002/004002001/004002001001/?Paging=1", ["name", "href", "ggstart_time", "info"]
        , add_info(f1, {"ggtype": "招标公告", "gctype": "工程类"}), f2],

    ["zfcg_zhaobiao_huowu_gg", "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004002/004002001/004002001002/?Paging=1",
     ["name", "href", "ggstart_time", "info"]
        , add_info(f1, {"ggtype": "招标公告", "gctype": "货物类"}), f2],

    ["zfcg_zhaobiao_fuwu_gg", "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004002/004002001/004002001003/?Paging=2", ["name", "href", "ggstart_time", "info"]
        , add_info(f1, {"ggtype": "招标公告", "gctype": "服务类"}), f2],

    ["zfcg_zhaobiao_quxian_gg", "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004002/004002001/004002001004/?Paging=1",
     ["name", "href", "ggstart_time", "info"]
        , add_info(f1, {"ggtype": "招标公告", "diqu": "区县信息"}), f2],

    ###政府采购-中标
    ["zfcg_zhongbiao_gc_gg", "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004002/004002004/004002004001/?Paging=1", ["name", "href", "ggstart_time", "info"]
        , add_info(f1, {"ggtype": "中标公告", "gctype": "工程类"}), f2],

    ["zfcg_zhongbiao_huowu_gg", "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004002/004002004/004002004002/?Paging=1",
     ["name", "href", "ggstart_time", "info"]
        , add_info(f1, {"ggtype": "中标公告", "gctype": "货物类"}), f2],

    ["zfcg_zhongbiao_fuwu_gg", "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004002/004002004/004002004003/?Paging=1",
     ["name", "href", "ggstart_time", "info"]
        , add_info(f1, {"ggtype": "中标公告", "gctype": "服务类"}), f2],

    ["zfcg_zhongbiao_quxian_gg", "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004002/004002004/004002004004/?Paging=1",
     ["name", "href", "ggstart_time", "info"]
        , add_info(f1, {"ggtype": "中标公告", "diqu": "区县信息"}), f2],

    ###政府采购-biangen
    ["zfcg_biangeng_gc_gg", "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004002/004002002/004002002001/?Paging=1", ["name", "href", "ggstart_time", "info"]
        , add_info(f1, {"ggtype": "中标公告", "gctype": "工程类"}), f2],

    ["zfcg_biangeng_huowu_gg", "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004002/004002002/004002002002/?Paging=1",
     ["name", "href", "ggstart_time", "info"]
        , add_info(f1, {"ggtype": "中标公告", "gctype": "货物类"}), f2],

    ["zfcg_biangeng_fuwu_gg", "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004002/004002002/004002002003/?Paging=1", ["name", "href", "ggstart_time", "info"]
        , add_info(f1, {"ggtype": "中标公告", "gctype": "服务类"}), f2],

    ["zfcg_biangeng_quxian_gg", "http://ggzy.yzcity.gov.cn/yzweb/jyxx/004002/004002002/004002002004/?Paging=1",
     ["name", "href", "ggstart_time", "info"]
        , add_info(f1, {"ggtype": "中标公告", "diqu": "区县信息"}), f2],

]


def work(conp, **args):
    gg_meta(conp, data=data, diqu="湖南省永州市", **args)

    gg_html(conp, f=f3, **args)
# work(conp=["postgres","since2015","127.0.0.1","hunan","yongzhou"])
