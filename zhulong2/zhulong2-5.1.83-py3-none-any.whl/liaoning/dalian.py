import pandas as pd
import re
from lxml import etree
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

from zhulong2.util.etl import est_meta, est_html, add_info

_name_ = 'liaoning_dalian'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//table[@id="tblInfo"]')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
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
    div = soup.find('table', id='tblInfo')
    return div


def f1(driver, num):
    time.sleep(0.3)
    locator = (By.XPATH, '//td[@id="MoreInfoList1_tdcontent"]/table/tbody/tr')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath(
        '//td[@id="MoreInfoList1_tdcontent"]/table/tbody/tr/td/a').get_attribute("href")[-50:]
    cnum = int(driver.find_element_by_xpath("//div[@id='MoreInfoList1_Pager']/table/tbody/tr[1]/td/font[3]").text)

    # print('val', val, 'cnum', cnum,'num',num)
    if int(cnum) != int(num):
        driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','%s')" % num)
        locator = (By.XPATH,
                   '//td[@id="MoreInfoList1_tdcontent"]/table/tbody/tr[1]/td/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//td[@id="MoreInfoList1_tdcontent"]/table/tbody/tr')
    for content in content_list:
        name = content.xpath("./td/a/text()")[0].strip()
        ggstart_time = content.xpath("./td[last()]/text()")[0].strip()
        url = "http://www.ccgp.dl.gov.cn" + content.xpath("./td/a/@href")[0]
        temp = [name, ggstart_time, url]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    time.sleep(0.3)
    locator = (By.XPATH, "//div[@id='MoreInfoList1_Pager']/table/tbody/tr/td/font[2]")
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    total_page = driver.find_element_by_xpath("//div[@id='MoreInfoList1_Pager']/table/tbody/tr/td/font[2]").text
    driver.quit()
    return int(total_page)


data = [

    ["zfcg_zhaobiao_shi_gg", "http://www.ccgp.dl.gov.cn/dlweb/003/003001/003001001/MoreInfo.aspx?CategoryNum=003001001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'市区'}), f2],
    ["zfcg_zhongbiao_shi_gg",
     "http://www.ccgp.dl.gov.cn/dlweb/003/003002/003002001/MoreInfo.aspx?CategoryNum=003002001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'市区'}), f2],
    ["zfcg_zhaobiao_danyilaiyuan_shi_gg",
     "http://www.ccgp.dl.gov.cn/dlweb/003/003004/003004001/MoreInfo.aspx?CategoryNum=003004001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'市区','method':'单一来源'}), f2],

    # 验收公示，需求公示，都无法访问
]

data1 = [
    'zfcg_zhaobiao_quxian_%s_gg;http://www.ccgp.dl.gov.cn/dlweb/003/003001/003001002/0030010020%s/MoreInfo.aspx?CategoryNum=0030010020%s',
    'zfcg_zhongbiao_quxian_%s_gg;http://www.ccgp.dl.gov.cn/dlweb/003/003002/003002002/0030020020%s/MoreInfo.aspx?CategoryNum=0030020020%s',
    'zfcg_zhaobiao_danyilaiyuan_quxian_%s_gg;http://www.ccgp.dl.gov.cn/dlweb/003/003004/003004002/0030040020%s/MoreInfo.aspx?CategoryNum=0030040020%s',
    ]


def new_url_list():
    for u in data1:
        url = iter(u % (x, x, x) for x in
                   ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16'])
        while 1:
            try:
                new_url_str = url.__next__().split(";")
                new_url_str.extend([["name", "ggstart_time", "href", "info"], f1, f2])
                data.append(new_url_str)
            except StopIteration:
                break



def work(conp, **arg):
    est_meta(conp, data=data, diqu="辽宁省大连市", **arg)
    est_html(conp, f=f3, **arg)


new_url_list()

if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "liaoning_dalian"],headless=False,pageloadstrategy='none')
