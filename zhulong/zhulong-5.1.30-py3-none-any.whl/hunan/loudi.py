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

_name_ = "loudi"


# driver=webdriver.Chrome()

# url="""http://ldggzy.hnloudi.gov.cn/jyxx/gcjs/?type=2"""

# driver.get(url)


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='layui-table-page']")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.CLASS_NAME, "layui-table-main")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = int(driver.find_element_by_class_name("layui-laypage-curr").text)
    if num != cnum:
        txt = driver.find_element_by_xpath("//div[contains(@class,'layui-table-main')]//tr[1]//a").get_attribute('href')[-40:]

        input1 = driver.find_element_by_class_name("layui-input")
        input1.clear()
        input1.send_keys(num)
        driver.find_element_by_class_name("layui-laypage-btn").click()

        locator = (By.XPATH, "//div[contains(@class,'layui-table-main')]//tr[1]//a[not(contains(@href,'%s'))]" % txt)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source

    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("div", class_="layui-table-main")

    trs = div.find_all("tr")
    data = []

    for tr in trs:
        tds = tr.find_all("td")
        tag = tds[0].text.strip()
        a = tds[1].find('a')
        href = "http://ldggzy.hnloudi.gov.cn" + a["href"]
        name = a['title']

        ggstart_time = tds[2].text.strip()
        info = json.dumps({"tag": tag}, ensure_ascii=False)
        tmp = [name, href, ggstart_time, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.CLASS_NAME, "layui-laypage-last")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = int(driver.find_element_by_class_name("layui-laypage-last").text)

    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    code = re.findall("code=(.*)&type", url)[0]
    locator = (By.XPATH, "//iframe[contains(@src,'%s')]" % code)

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    driver.switch_to.frame(driver.find_element_by_xpath("//iframe[contains(@src,'%s')]" % code))
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

    div = soup.find('div', class_='content')

    # div=div.find_all('div',class_='ewb-article')[0]

    return div


data = [
    ["gcjs_zhaobiao_gg", "http://ldggzy.hnloudi.gov.cn/jyxx/gcjs/?type=2", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_gqita_gg", "http://ldggzy.hnloudi.gov.cn/jyxx/gcjs/?type=3", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_zhongbiao_gg", "http://ldggzy.hnloudi.gov.cn/jyxx/gcjs/?type=4", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://ldggzy.hnloudi.gov.cn/jyxx/zfcg/?type=6", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_gqita_gg", "http://ldggzy.hnloudi.gov.cn/jyxx/zfcg/?type=7", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_zhongbiao_gg", "http://ldggzy.hnloudi.gov.cn/jyxx/zfcg/?type=8", ["name", "href", "ggstart_time", "info"], f1, f2],

]


# =["postgres","since2015","127.0.0.1","hunan","loudi"]
def work(conp, **args):
    est_meta(conp, data=data, diqu="湖南省娄底市", **args)

    est_html(conp, f=f3, **args)

# work(conp=["postgres","since2015","127.0.0.1","hunan","loudi"])
