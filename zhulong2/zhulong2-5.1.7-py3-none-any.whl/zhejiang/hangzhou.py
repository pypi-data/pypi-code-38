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

_name_ = 'zhejiang_hangzhou'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='detail_con'][string-length()>10]")
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
    div = soup.find('div', class_='detail_con')
    return div


def f1(driver, num):
    locator = (By.XPATH, '/html/body/div[2]/div/table/tbody/tr[1]/td[2]/div/ul/li[1]/a')
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('/html/body/div[2]/div/table/tbody/tr[1]/td[2]/div/ul/li[1]/a').get_attribute(
        "href")[-30:]
    try:
        cnum = re.findall(r'(\d+)/', driver.find_element_by_xpath(
            '/html/body/div[2]/div/table/tbody/tr[1]/td[2]/div/div[3]/span[1]').getattribute("content").text)[0]
    except:
        cnum = 1
    # print('val', val, 'cnum', cnum)
    if int(cnum) != int(num):
        driver.execute_script("javascript:toPage(%s);" % num)
        locator = (
        By.XPATH, '/html/body/div[2]/div/table/tbody/tr[1]/td[2]/div/ul/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('/html/body/div[2]/div/table/tbody/tr[1]/td[2]/div/ul/li')
    for content in content_list:
        name = content.xpath("./a/text()")[1].strip()
        ggstart_time = content.xpath('./span/text()')[0].strip()
        href = 'http://cg.hzft.gov.cn/' + content.xpath("./a/@href")[0].strip()
        temp = [name, ggstart_time, href]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '/html/body/div[2]/div/table/tbody/tr[1]/td[2]/div/div[3]/span[1]')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    try:
        total_page = re.findall(r'/(\d+)', driver.find_element_by_xpath(
            '/html/body/div[2]/div/table/tbody/tr[1]/td[2]/div/div[3]/span[1]').text)[0]
    except:
        total_page = 1
    # print('total_page', total_page)
    driver.quit()
    return int(total_page)


data = [
    #
    ["zfcg_zhaobiao_gg", "http://cg.hzft.gov.cn/www/noticelist.do?noticetype=3,3001,3002,3008,3009,3011,3014,4001,4002",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_xunjia_gg", "http://cg.hzft.gov.cn/www/noticelist.do?noticetype=7,3003",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'询价'}), f2],
    ["zfcg_zhaobiao_danyilaiyuan_gg", "http://cg.hzft.gov.cn/www/noticelist.do?noticetype=1,3012",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'单一来源'}), f2],
    ["zfcg_zhaobiao_zhengxun_gg", "http://cg.hzft.gov.cn/www/noticelist.do?noticetype=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'征询'}), f2],
    ["zfcg_biangeng_gg", "http://cg.hzft.gov.cn/www/noticelist.do?noticetype=4,15,3005,3006,4003",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://cg.hzft.gov.cn/www/noticelist.do?noticetype=5,6,3004,3007,3017",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="浙江省杭州市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "zhejiang_hangzhou"])
