import json

import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

from zhulong.util.etl import est_meta, est_html, add_info

_name_ = 'shenzhen'


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, "//div[@id='div_print']")
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
    div = soup.find('div', id='div_print')

    return div


def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="list"]/li[1]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//ul[@class="list"]/li[1]/a').get_attribute("href")[-30:]
    cnum = re.findall('(\d+)', driver.find_element_by_xpath('//div[@class="fanye"]/font[last()]').text)[0]
    if int(cnum) != int(num):
        newUrl = re.sub('index[_\d]*\.','index.' if num == 1 else 'index_'+str(int(num)-1)+'.',driver.current_url)
        driver.get(newUrl)
        locator = (By.XPATH, '//ul[@class="list"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@class="list"]/li')

    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        ggstart_time = content.xpath("./small/text()")[0].strip()
        href = driver.current_url.rsplit('/',maxsplit=1)[0] +  content.xpath("./a/@href")[0].strip().strip('.')
        temp = [name, ggstart_time, href]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="fanye"]/font[last()-1]')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    total_page = re.findall('(\d+)', driver.find_element_by_xpath('//div[@class="fanye"]/font[last()-1]').text)[0]
    driver.quit()
    return int(total_page)


data = [

    ["gcjs_zhaobiao_gg",
     "http://ggzy.sz.gov.cn/jyxx/gzjsztb/zbgg/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_kongzhijia_gg",
     "http://ggzy.sz.gov.cn/jyxx/gzjsztb/zbkzjgs/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["gcjs_kaibiao_gg",
     "http://ggzy.sz.gov.cn/jyxx/gzjsztb/kbqkgs/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://ggzy.sz.gov.cn/jyxx/gzjsztb/zbjggs/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_pingbiao_gg",
     "http://ggzy.sz.gov.cn/jyxx/gzjsztb/pbbggs/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'评标'}), f2],
    ["gcjs_gqita_dingbiao_gg",
     "http://ggzy.sz.gov.cn/jyxx/gzjsztb/dbjggs/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'定标'}), f2],
    ["gcjs_zgysjg_gg",
     "http://ggzy.sz.gov.cn/jyxx/gzjsztb/zsjyjgs/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_gg",
     "http://ggzy.sz.gov.cn/jyxx/zfcgxm/zbgg_zf/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://ggzy.sz.gov.cn/jyxx/zfcgxm/zbcjgg_zf/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_zhaobiao_gg",
     "http://ggzy.sz.gov.cn/jyxx/qtggzyjy/jygg/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'其他'}), f2],
    ["zfcg_qita_zhongbiao_gg",
     "http://ggzy.sz.gov.cn/jyxx/qtggzyjy/jggs/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'其他'}), f2],


]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="广东省深圳市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "guangdong_shenzhen"])
