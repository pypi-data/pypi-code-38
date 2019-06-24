import json

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write, db_query, db_command
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from zhulong.util.etl import est_meta, est_html, add_info
import time

_name_ = "huanggang"


def f1(driver, num):
    locator = (By.CLASS_NAME, "myGVClass ")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    if driver.find_element_by_xpath("//select/option[@selected]").text != "每页显示100条":
        driver.find_element_by_id("ctl00_ContentPlaceHolder1_DDLPageSize").send_keys("每页显示100条")

    locator = (By.XPATH, "//select/option[@selected][string()='每页显示100条']")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cur_num = int(driver.find_element_by_id("ctl00_ContentPlaceHolder1_myGV_ctl103_LabelCurrentPage").text)
    val = driver.find_element_by_xpath("//table[@class='myGVClass ']//tr[@class='myGVAltRow '][1]/td[2]").text

    if num != cur_num:
        if num > cur_num:
            dt = num - cur_num
            # 点击下页dt次
            while dt > 0:
                dt -= 1
                driver.find_element_by_id("ctl00_ContentPlaceHolder1_myGV_ctl103_LinkButtonNextPage").click()
                locator = (By.XPATH, "//table[@class='myGVClass ']//tr[@class='myGVAltRow '][1]/td[2][string()!='%s']" % val)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
                val = driver.find_element_by_xpath("//table[@class='myGVClass ']//tr[@class='myGVAltRow '][1]/td[2]").text
        else:
            dt = cur_num - num
            while dt > 0:
                dt -= 1
                driver.find_element_by_id("ctl00_ContentPlaceHolder1_myGV_ctl103_LinkButtonPreviousPage").click()
                locator = (By.XPATH, "//table[@class='myGVClass ']//tr[@class='myGVAltRow '][1]/td[2][string()!='%s']" % val)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
                val = driver.find_element_by_xpath("//table[@class='myGVClass ']//tr[@class='myGVAltRow '][1]/td[2]").text

    page = driver.page_source

    soup = BeautifulSoup(page, "html.parser")

    table = soup.find("table", class_="myGVClass")

    trs = table.find_all("tr", class_="myGVAltRow")
    data1 = []
    for tr in trs:
        ggcode, name = [td.text.strip() for td in tr.find_all("td")]

        a = tr.find("a")
        href = "http://ggzy.hg.gov.cn/ceinwz/" + a["href"]

        ggstart_time = '-'
        info = json.dumps({'项目编号': ggcode}, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]
        data1.append(tmp)
        # print(tmp)
    df = pd.DataFrame(data=data1)
    return df


def f2(driver):
    if driver.find_element_by_xpath("//select/option[@selected]").text != "每页显示100条":
        driver.find_element_by_id("ctl00_ContentPlaceHolder1_DDLPageSize").send_keys("每页显示100条")

    locator = (By.XPATH, "//select/option[@selected][string()='每页显示100条']")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.ID, "ctl00_ContentPlaceHolder1_myGV_ctl103_LabelPageCount")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = int(driver.find_element_by_id("ctl00_ContentPlaceHolder1_myGV_ctl103_LabelPageCount").text)
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)
    try:
        locator = (By.CLASS_NAME, "yygl")

        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    except:
        locator = (By.XPATH, '//td[@class="tb2"]')
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

    div = soup.find('table', class_='yygl')
    if not div:
        div = soup.find('td', class_='tb2')

    return div


data = [
    ["gcjs_gqita_zhao_zhong_gg", "http://ggzy.hg.gov.cn/ceinwz/WebInfo_List.aspx?&newsid=700&jsgc=0100000&zbdl=1&FromUrl=jygg",
     ["name", 'ggstart_time', "href", "info"], f1, f2],
    ["zfcg_gqita_zhao_zhong_liu_bian_gg", "http://ggzy.hg.gov.cn/ceinwz/WebInfo_List.aspx?&newsid=400&zfcg=0100000&FromUrl=jygg",
     ["name", 'ggstart_time', "href", "info"], f1, f2]
]


def work(conp, **args):
    est_meta(conp, data, diqu="湖北省黄冈市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "hubei", "huanggang"])
    # driver = webdriver.Chrome()
    # driver.get('http://ggzy.hg.gov.cn/ceinwz/WebInfo_List.aspx?&newsid=700&jsgc=0100000&zbdl=1&FromUrl=jygg')
    # f1(driver,2)
    # print(f3(driver, 'http://ggzy.hg.gov.cn/ceinwz/admin_show.aspx?id=7153'))

    # driver.quit()
