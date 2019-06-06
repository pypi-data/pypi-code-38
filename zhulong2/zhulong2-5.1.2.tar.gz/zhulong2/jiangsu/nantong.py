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

_name_ = 'jiangsu_nantong'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@width='100%' and @class='']|//table[@width='100%']")
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
    div = soup.findAll('table', width='100%')
    return div


def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='list-ul']/li[1]/a")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//ul[@class='list-ul']/li[1]/a").get_attribute("href")[-40:]

    cnum = driver.find_element_by_xpath("//input[@class='default_pgCurrentPage']").get_attribute("value")
    # print('val', val, 'cnum', cnum)
    if int(cnum) != int(num):
        driver.find_element_by_xpath("//input[@class='default_pgCurrentPage']").clear()
        driver.find_element_by_xpath("//input[@class='default_pgCurrentPage']").send_keys(num)
        driver.find_element_by_xpath('//li[@class="default_pgJump active"]').click()
        locator = (By.XPATH, '//ul[@class="list-ul"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//ul[@class='list-ul']/li")
    for content in content_list:
        name = content.xpath("./a/span/text()")[0].strip()
        ggstart_time = content.xpath('./span/text()')[0].strip()
        href = "http://zfcg-bak.nantong.gov.cn" + content.xpath("./a/@href")[0].strip('.')
        temp = [name, ggstart_time, href]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//span[@class='default_pgTotalPage']")
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    total_page = driver.find_element_by_xpath("//span[@class='default_pgTotalPage']").text

    # print('total_page', total_page)
    driver.quit()
    return int(total_page)


data = [
    #
    ["zfcg_zhaobiao_gongkai_gg", "http://zfcg-bak.nantong.gov.cn/ntszfcgw/gkzb/gkzb.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'公开'}), f2],
    ["zfcg_zhaobiao_tanpan_gg", "http://zfcg-bak.nantong.gov.cn/ntszfcgw/jzxtp/jzxtp.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'谈判'}), f2],
    ["zfcg_zhaobiao_cuoshang_gg", "http://zfcg-bak.nantong.gov.cn/ntszfcgw/jzxcs/jzxcs.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'磋商'}), f2],
    ["zfcg_zhaobiao_danyilaiyuan_gg", "http://zfcg-bak.nantong.gov.cn/ntszfcgw/dyly/dyly.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'单一来源'}), f2],
    ["zfcg_zhaobiao_xunjia_gg", "http://zfcg-bak.nantong.gov.cn/ntszfcgw/wsxj/wsxj.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'询价'}), f2],
    ["zfcg_zhaobiao_jingjia_gg", "http://zfcg-bak.nantong.gov.cn/ntszfcgw/wsjj/wsjj.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'竞价'}), f2],
    ["zfcg_zhaobiao_bumenxianqu_gg", "http://zfcg-bak.nantong.gov.cn/ntszfcgw/bmxqcggg/bmxqcggg.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'部门县区'}), f2],

    ["zfcg_zhaobiao_gqita_gg", "http://zfcg-bak.nantong.gov.cn/ntszfcgw/qtxj/qtxj.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://zfcg-bak.nantong.gov.cn/ntszfcgw/jggs/jggs.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="江苏省南通市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "jiangsu_nantong"])
