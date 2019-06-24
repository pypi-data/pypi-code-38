import json

import pandas as pd
import re

import requests
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

from zhulong2.util.etl import est_meta, est_html, add_info
from zhulong2.util.fake_useragent import UserAgent

_name_ = 'heilongjiang_shenghui'
cookies = ''
form_data1 ={}
form_data = {
    # 'lbbh': '4',
    'id': '110',
    'xwzsPage.zlbh': '',
}
ua = UserAgent()
headers = {

    'Cookie': 'COLLCK=1735242673;JSESSIONID=0hyjcvGTnnQ1GQbHqyBPLcQtpBlWQJRJZNx7ypskCwXktyDly255!-1523611838;',
    'User-Agent': ua.random,

}


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, "//div[@class='xxej']")
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
    div = soup.find('div', class_='xxej')

    return div


def f1(driver, num):
    '''{
    'xwzsPage.pageNo': '1',
    'xwzsPage.pageSize': '20',
    'xwzsPage.pageCount': '1514',
    'lbbh': '4',
    'id': '110',
    'xwzsPage.LBBH': '4',
    }'''
    
    form_data1['xwzsPage.pageNo'] = num
    url = driver.current_url.split('?')[0]
    response = requests.post(url, headers=headers, data=form_data1,timeout=40).text


    data = []

    body = etree.HTML(response)
    content_list = body.xpath('//div[@class="yahoo"]/div')

    for content in content_list:
        name = content.xpath("./span/a/text()")[0].strip()
        ggstart_time = content.xpath("./span[2]/text()")[0].strip()
        href = 'http://www.hljcg.gov.cn' + re.findall(r"href='([^']+)'", content.xpath("./span/a/@onclick")[0])[0]
        temp = [name, ggstart_time, href]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    global cookies,form_data1
    form_data1 = form_data.copy()
    lbbh = driver.current_url.split('?')[1]
    url = driver.current_url.split('?')[0]

    home_url = 'http://www.hljcg.gov.cn/home.jsp'
    driver.get(home_url)

    driver.execute_script('window.scrollBy(250,0)')

    driver.find_element_by_class_name('sbj_btn').click()

    cookies = ''
    for dict1 in driver.get_cookies():
        cookies += dict1['name'] + '='
        cookies += dict1['value'] + ';'

    headers['Cookie'] = cookies
    form_data1['lbbh'] = lbbh
    response = requests.post(url, headers=headers, data=form_data1,timeout=40).text
    body = etree.HTML(response)

    total_page = re.findall('/(\d+)', body.xpath('//div[@class="list-page-detail"]/span/b[2]/text()')[0])[0]
    driver.quit()
    form_data1['xwzsPage.pageCount'] = total_page
    form_data1['xwzsPage.pageSize'] = 20
    form_data1['xwzsPage.LBBH'] = lbbh
    form_data1['xwzsPage.GJZ'] = ''

    return int(total_page)


data = [
    # http://www.hljcg.gov.cn/xwzs!queryGd.action?4
    ["zfcg_zhaobiao_gg", "http://www.hljcg.gov.cn/xwzs!queryGd.action?4",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_yucai_gg", "http://www.hljcg.gov.cn/xwzs!queryGd.action?99",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://www.hljcg.gov.cn/xwzs!queryGd.action?5",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # biangeng 包括流标废标
    ["zfcg_gqita_bian_liu_gg", "http://www.hljcg.gov.cn/xwzs!queryGd.action?30",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_danyilaiyuan_gg", "http://www.hljcg.gov.cn/xwzs!queryGd.action?98",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'method': '单一来源'}), f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="黑龙江省", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "heilongjiang"], pageloadtimeout=60,pageloadstrategy='none')

