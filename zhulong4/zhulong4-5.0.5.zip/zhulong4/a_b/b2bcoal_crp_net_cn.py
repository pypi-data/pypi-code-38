import json
import math
import random
import re

import requests
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong4.util.etl import est_html, est_meta, add_info, est_meta_large
import time

_name_ = 'b2bcoal_crp_net_cn'


def f1(driver, num):
    time.sleep(random.randint(1,3))
    locator = (By.XPATH, '//table[@id="ctl00_ContentPlaceHolder1_gvTenderList"]/tbody/tr[contains(@class,"tr")]/td/a')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath(
        '//table[@id="ctl00_ContentPlaceHolder1_gvTenderList"]/tbody/tr[contains(@class,"tr")][1]/td/a').text
    cnum_temp = driver.find_element_by_xpath('//div[@id="ctl00_ContentPlaceHolder1_pager"]').text
    cnum = re.findall('第(\d+)页', cnum_temp)[0]

    if int(cnum) != int(num):
        driver.execute_script("javascript:__doPostBack('ctl00$ContentPlaceHolder1$pager','%s')" % num)
        locator = (By.XPATH,
                   '//table[@id="ctl00_ContentPlaceHolder1_gvTenderList"]/tbody/tr[contains(@class,"tr")][1]/td/a[not(contains(@href,"%s"))]' % val)
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@id="ctl00_ContentPlaceHolder1_gvTenderList"]/tbody/tr[contains(@class,"tr")]')
    for content in content_list:
        name = content.xpath("./td[2]/text()")[0].strip()
        type, tender_code, pre, flag = re.findall('\'([^\']+)\'', content.xpath("./td[1]/a/@onclick")[0])
        url = 'http://b2bcoal.crp.net.cn/pub_v2/Tender/TenderItem.aspx?type=' + type + '&pre' + pre + '&TenderCode=' + tender_code
        ggstart_time = content.xpath("./td[last()-1]/text()")[0].strip()
        ggend_time = content.xpath("./td[last()]/text()")[0].strip()
        status = content.xpath('./td[last()-2]/span')[0].xpath('string(.)')
        inquiry_project = content.xpath('./td[3]/span/text()')[0].strip()
        info = json.dumps({"status":status,'tender_code':tender_code,'ggend_time':ggend_time,"inquiry_project":inquiry_project},ensure_ascii=False)
        temp = [name, ggstart_time, url,info ]
        data.append(temp)
        # print('temp', temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@id="ctl00_ContentPlaceHolder1_pager"]/table/tbody/tr')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_temp = driver.find_element_by_xpath('//div[@id="ctl00_ContentPlaceHolder1_pager"]').text
    total_page = re.findall('共(\d+)页', total_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//table[@cellspacing="5"]')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('table', cellspacing='5')
    return div


data = [
    ["qy_zhaobiao_gg",
     "http://b2bcoal.crp.net.cn/Tender/ShowTenderList.aspx?type=Inquiry&mode=-1&pre=0",
     ["name", "ggstart_time", "href","info"], f1, f2],
    ["qy_zhaobiao_wz_gg",
     "http://b2bcoal.crp.net.cn/Tender/ShowTenderList.aspx?type=Tender&mode=-1&pre=0",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"Tag":"物资"}), f2],

    ["qy_zhaobiao_gcfw_gg",
     "http://b2bcoal.crp.net.cn/Tender/ShowTenderList.aspx?type=ProInquiry&mode=-1&pre=0",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"Tag":"工程服务"}), f2],

    ["qy_zhongbiao_gg",
     "http://b2bcoal.crp.net.cn/Tender/ShowTenderList.aspx?mode=7&pre=0",
     ["name", "ggstart_time", "href","info"], f1, f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="华润煤业", **args)
    est_html(conp, f=f3, **args)


def main():
    conp = ["postgres", "since2015", "192.168.3.171", "anbang_qiye", "b2bcoal_crp_net_cn"]
    work(conp,pageloadtimeout=40)
    # driver = webdriver.Chrome()
    # driver.get("http://b2bcoal.crp.net.cn/Tender/ShowTenderList.aspx?type=Inquiry&mode=-1&pre=0")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 10)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # driver.get("http://b2bcoal.crp.net.cn/Tender/ShowTenderList.aspx?type=ProInquiry&mode=-1&pre=0")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 10)
    # driver = webdriver.Chrome()
    # driver.get("http://b2bcoal.crp.net.cn/Tender/ShowTenderList.aspx?mode=7&pre=0")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 10)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(
    #     f3(driver, 'http://b2bcoal.crp.net.cn/pub_v2/Tender/TenderItem.aspx?type=Inquiry&pre=0&TenderCode=MYZT028380'))
    # driver.close()
if __name__ == "__main__":
    main()