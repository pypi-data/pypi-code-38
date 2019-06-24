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
from zhulong.util.etl import gg_meta, gg_html, est_tables, gg, est_meta, est_html, add_info

_name_ = "chenzhou"


# driver=webdriver.Chrome()

# url="""http://www.app.czs.gov.cn/czggzy/18360/18370/18371/18382/18383/index.jsp?pager.offset=0&pager.desc=false"""

# driver.get(url)


def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='clearfix list-ul']//li[2]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url = driver.current_url
    cnum = int(int(re.findall("pager.offset=([0-9]*)", url)[0]) / 15) + 1
    if cnum != num:
        val = driver.find_element_by_xpath("//ul[@class='clearfix list-ul']//li[2]//a").get_attribute("href")[-20:]

        num = (num - 1) * 15
        url = re.sub("pager.offset=[0-9]*", "pager.offset=%d" % num, url)

        driver.get(url)

        locator = (By.XPATH, "//ul[@class='clearfix list-ul']//li[2]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    ul = soup.find("ul", class_="list-ul")

    lis = ul.find_all("li")
    data = []

    for li in lis:
        span = li.find("span")
        a = li.find("a")
        tmp = [a["title"], a["href"], span.text.strip()]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//ul[@class='clearfix list-ul']//li[2]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//ul[@class='pager']/li[last()]/a[string()='尾页']")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    txt = driver.find_element_by_xpath("//ul[@class='pager']/li[last()]/a[string()='尾页']").get_attribute("href")

    total = int(re.findall("ager.offset=([0-9]*)", txt)[0])

    total = int(total / 15) + 1

    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.CLASS_NAME, "arc")

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

    div = soup.find('div', class_='arc')
    # div=div.find_all('div',class_='ewb-article')[0]

    return div


def add(f, info):
    def wrap(*krg):
        driver = krg[0]

        if f == f1:
            df = f(*krg)
            df[df.columns[-1]] = json.dumps(info, ensure_ascii=False)
            return df
        else:
            return f(*krg)

    return wrap


data = [

    ["gcjs_fangwushizheng_zhaobiao_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18371/18382/18383/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "href", "ggstart_time", "info"], add(f1, {"xmtype": "房建市政"}), f2],

    ["gcjs_jiaotong_zhaobiao_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18371/18382/18384/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "href", "ggstart_time", "info"], add(f1, {"xmtype": "交通工程"}), f2],

    ["gcjs_shuili_zhaobiao_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18371/18382/18385/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "href", "ggstart_time", "info"], add(f1, {"xmtype": "水利工程"}), f2],

    ["gcjs_qita_zhaobiao_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18371/18382/18386/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "href", "ggstart_time", "info"], add(f1, {"xmtype": "其它"}), f2],

    ["gcjs_gqita_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18371/18382/18387/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "href", "ggstart_time", "info"], add(f1, {"ggtype": "代理公告"}), f2],

    ["gcjs_zhongbiao_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18371/18392/18393/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_zhongbiao_daili_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18371/18394/18395/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "href", "ggstart_time", "info"], add(f1, {"ggtype": "中标代理公示"}), f2],

    ##政府采购 招标
    ["zfcg_zhaobiao_zb1_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18372/18396/18397/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "href", "ggstart_time", "info"], add(f1, {"zhaobiaofs": "公开招标"}), f2],

    ["zfcg_zhaobiao_zb2_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18372/18396/18398/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "href", "ggstart_time", "info"], add(f1, {"zhaobiaofs": "竞争性谈判"}), f2],

    ["zfcg_zhaobiao_zb3_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18372/18396/18399/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "href", "ggstart_time", "info"], add(f1, {"zhaobiaofs": "询价"}), f2],

    ["zfcg_zhaobiao_zb4_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18372/18396/18400/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "href", "ggstart_time", "info"], add(f1, {"zhaobiaofs": "单一来源"}), f2],

    ##政府采购  中标

    ["zfcg_zhongbiao_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18372/18406/18407/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_liubiao_gg",
     "http://www.app.czs.gov.cn/czggzy/18360/18370/18372/18406/18408/index.jsp?pager.offset=0&pager.desc=false",
     ["name", "href", "ggstart_time", "info"], f1, f2]

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖南省郴州市", **args)
    est_html(conp, f=f3, **args)


# est_tables(conp=["postgres","since2015","127.0.0.1","hunan","chenzhou"],data=data[6:])
if __name__ == '__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "hunan", "chenzhou"]
    work(conp,num=3)
