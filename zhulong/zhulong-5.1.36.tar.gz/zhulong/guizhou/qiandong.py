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

_name_ = "qiandong"


def f1(driver, num):
    locator = (By.XPATH, '//table[@id="MoreInfoList1_DataGrid1"]//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum=int(driver.find_element_by_xpath('//div[@id="MoreInfoList1_Pager"]//font[@color="red"]').text)

    if cnum != num:
        val = driver.find_element_by_xpath('//table[@id="MoreInfoList1_DataGrid1"]//tr[1]//a').get_attribute('href')[-40:-10]
        driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','%s')"%num)
        locator = (By.XPATH, '//table[@id="MoreInfoList1_DataGrid1"]//tr[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    divs = soup.find("table",id="MoreInfoList1_DataGrid1").find_all('tr')

    data = []
    for div in divs:
        name = div.find("a")['title']
        href = div.find("a")['href']
        ggstart_time = div.find("td", class_="webinfodate").get_text().strip()
        if 'http' in href:
            href=href
        else:
            href='http://www.qdnggzy.cn' + href

        tmp = [name, href, ggstart_time]

        print(tmp)
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df

def f2(driver):
    locator = (By.XPATH, '//table[@id="MoreInfoList1_DataGrid1"]//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        total = int(driver.find_element_by_xpath('//div[@id="MoreInfoList1_Pager"]//font[@color="blue"][2]').text)

    except:
        total = 1
    driver.quit()

    return total




def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//table[@class="tbinfofont"][string-length()>50]')
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

    div = soup.find('table', class_='tbinfofont').parent.parent

    return div


data = [
    ["gcjs_zhaobiao_gg", "http://www.qdnggzy.cn/qdnztb/jyxx/056001/056001001/MoreInfo.aspx?CategoryNum=056001001",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_gqita_da_bian_gg", "http://www.qdnggzy.cn/qdnztb/jyxx/056001/056001002/MoreInfo.aspx?CategoryNum=056001002",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg", "http://www.qdnggzy.cn/qdnztb/jyxx/056001/056001004/MoreInfo.aspx?CategoryNum=056001004",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_liubiao_gg", "http://www.qdnggzy.cn/qdnztb/jyxx/056001/056001005/MoreInfo.aspx?CategoryNum=056001005",
     ["name", "href", "ggstart_time", "info"], f1, f2],
    ["gcjs_zgys_gg", "http://www.qdnggzy.cn/qdnztb/jyxx/056001/056001006/MoreInfo.aspx?CategoryNum=056001006",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_zgysjg_gg", "http://www.qdnggzy.cn/qdnztb/jyxx/056001/056001007/MoreInfo.aspx?CategoryNum=056001007",
     ["name", "href", "ggstart_time", "info"], f1, f2],

   ["zfcg_zhaobiao_gg", "http://www.qdnggzy.cn/qdnztb/jyxx/056002/056002001/MoreInfo.aspx?CategoryNum=056002001",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_biangeng_gg", "http://www.qdnggzy.cn/qdnztb/jyxx/056002/056002002/MoreInfo.aspx?CategoryNum=056002002",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_zhongbiao_gg", "http://www.qdnggzy.cn/qdnztb/jyxx/056002/056002003/MoreInfo.aspx?CategoryNum=056002003",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_liubiao_gg", "http://www.qdnggzy.cn/qdnztb/jyxx/056002/056002004/MoreInfo.aspx?CategoryNum=056002004",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_yucai_gg", "http://www.qdnggzy.cn/qdnztb/jyxx/056002/056002007/MoreInfo.aspx?CategoryNum=056002007",
     ["name", "href", "ggstart_time", "info"], f1, f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="贵州省黔东南州", **args)

    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guizhou", "qiandong"], pageloadstrategy='none',num=1,total=2)