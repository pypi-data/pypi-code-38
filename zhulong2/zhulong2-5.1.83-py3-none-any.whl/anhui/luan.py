import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

from zhulong2.util.etl import est_meta, est_html, add_info

_name_ = 'anhui_luan'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='myPrintArea']")
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
    div = soup.find('div', id='myPrintArea')
    return div


def f1(driver, num):
    url = driver.current_url
    channel_code = re.findall(r'channelCode=(\w+?)&', url)[0]
    locator = (By.XPATH, "//div[@name='%s']/ul/li[1]" % channel_code)
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//div[@name='%s']/ul/li[1]/a" % channel_code).get_attribute("href")[-30:]
    cnum = re.findall(r'(\d+)/', driver.find_element_by_xpath('//*[@id="QuotaList_paginate"]/span[1]').text)[0]
    # print('val', val, 'cnum', cnum)
    if int(cnum) != int(num):
        url = driver.current_url
        url1 = re.sub(r"page=\d+", 'page=' + str(num), url)
        driver.get(url1)
        locator = (By.XPATH, '//div[@name="%s"]/ul/li[1]/a[not(contains(@href,"%s"))] ' % (channel_code, val))
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@name='%s']/ul/li" % channel_code)

    for content in content_list:
        ggstart_time = content.xpath('./span/text()')[0].strip()
        name = content.xpath("./a/text()")[1].strip()
        href = 'http://www.lazfcg.cn' + content.xpath("./a/@href")[0].strip()
        temp = [name, ggstart_time, href]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//*[@id="QuotaList_paginate"]/span[1]')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    total_page = re.findall(r'/(\d+)', driver.find_element_by_xpath('//*[@id="QuotaList_paginate"]/span[1]').text)[0]
    driver.quit()
    return int(total_page)


data = [
    ["zfcg_zhaobiao_tanpan_shiji_gg",
     "http://www.lazfcg.cn/CmsNewsController.do?method=newsList&channelCode=zfcg_1030&sign=shiji&parentCode=zfcg_TQ10&page=1&rp=20&param=bulletin&id=zfcg_1030",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '市级', 'method': '谈判'}), f2],

    ["zfcg_zhaobiao_cuoshang_shiji_gg",
     "http://www.lazfcg.cn/CmsNewsController.do?method=newsList&channelCode=zfcg_10310&sign=shiji&parentCode=zfcg_TQ10&page=1&rp=20&param=bulletin&id=zfcg_10310",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '市级', 'method': '磋商'}), f2],

    ["zfcg_zhaobiao_xunjia_shiji_gg",
     "http://www.lazfcg.cn/CmsNewsController.do?method=newsList&channelCode=zfcg_1020&sign=shiji&parentCode=zfcg_TQ10&page=1&rp=20&param=bulletin&id=zfcg_1020",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '市级', 'method': '询价'}), f2],

    ["zfcg_zhaobiao_gongkai_shiji_gg",
     "http://www.lazfcg.cn/CmsNewsController.do?method=newsList&channelCode=zfcg_1010&sign=shiji&parentCode=zfcg_TQ10&page=1&rp=20&param=bulletin&id=zfcg_1010",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '市级', 'method': '公开'}), f2],

    ["zfcg_zhaobiao_danyilaiyuan_shiji_gg",
     "http://www.lazfcg.cn/CmsNewsController.do?method=newsList&channelCode=zfcg_1040&sign=shiji&parentCode=zfcg_TQ10&page=1&rp=20&param=bulletin&id=zfcg_1040",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '市级', 'method': '单一来源'}), f2],

    ["zfcg_zhaobiao_yaoqing_shiji_gg",
     "http://www.lazfcg.cn/CmsNewsController.do?method=newsList&channelCode=zfcg_1050&sign=shiji&parentCode=zfcg_TQ10&page=1&rp=20&param=bulletin&id=zfcg_1050",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '市级', 'method': '邀请'}), f2],

    ["zfcg_biangeng_shiji_gg",
     "http://www.lazfcg.cn/CmsNewsController.do?method=newsList&channelCode=zfcg_1100&sign=shiji&parentCode=sjcg&page=1&rp=20&param=bulletin&id=zfcg_1100",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '市级'}), f2],

    ["zfcg_zhongbiao_lx1_shiji_gg",
     "http://www.lazfcg.cn/CmsNewsController.do?method=newsList&channelCode=zfcg_1120&sign=shiji&parentCode=sjcg&page=1&rp=20&param=bulletin&id=zfcg_1120",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '市级', 'Tag': '成交'}), f2],

    ["zfcg_zhongbiao_shiji_gg",
     "http://www.lazfcg.cn/CmsNewsController.do?method=newsList&channelCode=zfcg_1080&sign=shiji&parentCode=sjcg&page=1&rp=20&param=bulletin&id=zfcg_1080",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '市级'}), f2],

    ["zfcg_liubiao_shiji_gg",
     "http://www.lazfcg.cn/CmsNewsController.do?method=newsList&channelCode=zfcg_1130&sign=shiji&parentCode=sjcg&page=1&rp=20&param=bulletin&id=zfcg_1130",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '市级'}), f2],

    ["zfcg_zhaobiao_tanpan_xianji_gg",
     "http://www.lazfcg.cn/CmsNewsController.do?method=newsList&channelCode=zfcg_1030&sign=&parentCode=zfcg_TQ10&page=1&rp=20&param=bulletin&id=zfcg_1030",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '县级', 'method': '谈判'}), f2],

    ["zfcg_zhaobiao_cuoshang_xianji_gg",
     "http://www.lazfcg.cn/CmsNewsController.do?method=newsList&channelCode=zfcg_10310&sign=&parentCode=zfcg_TQ10&page=1&rp=20&param=bulletin&id=zfcg_10310",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '县级', 'method': '磋商'}), f2],

    ["zfcg_zhaobiao_xunjia_xianji_gg",
     "http://www.lazfcg.cn/CmsNewsController.do?method=newsList&channelCode=zfcg_1020&sign=&parentCode=zfcg_TQ10&page=1&rp=20&param=bulletin&id=zfcg_1020",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '县级', 'method': '询价'}), f2],

    ["zfcg_zhaobiao_gongkai_xianji_gg",
     "http://www.lazfcg.cn/CmsNewsController.do?method=newsList&channelCode=zfcg_1010&sign=&parentCode=zfcg_TQ10&page=1&rp=20&param=bulletin&id=zfcg_1010",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '县级', 'method': '公开'}), f2],

    ["zfcg_zhaobiao_danyilaiyuan_xianji_gg",
     "http://www.lazfcg.cn/CmsNewsController.do?method=newsList&channelCode=zfcg_1040&sign=&parentCode=zfcg_TQ10&page=1&rp=20&param=bulletin&id=zfcg_1040",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '县级', 'method': '单一来源'}), f2],

    ["zfcg_zhaobiao_yaoqing_xianji_gg",
     "http://www.lazfcg.cn/CmsNewsController.do?method=newsList&channelCode=zfcg_1050&sign=&parentCode=zfcg_TQ10&page=1&rp=20&param=bulletin&id=zfcg_1050",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '县级', 'method': '邀请'}), f2],

    ["zfcg_biangeng_xianji_gg",
     "http://www.lazfcg.cn/CmsNewsController.do?method=newsList&channelCode=zfcg_1100&sign=&parentCode=sjcg&page=1&rp=20&param=bulletin&id=zfcg_1100",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '县级'}), f2],

    ["zfcg_zhongbiao_lx1_xianji_gg",
     "http://www.lazfcg.cn/CmsNewsController.do?method=newsList&channelCode=zfcg_1120&sign=&parentCode=sjcg&page=1&rp=20&param=bulletin&id=zfcg_1120",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '县级', 'Tag': '成交'}), f2],

    ["zfcg_zhongbiao_xianji_gg",
     "http://www.lazfcg.cn/CmsNewsController.do?method=newsList&channelCode=zfcg_1080&sign=&parentCode=sjcg&page=1&rp=20&param=bulletin&id=zfcg_1080",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '县级'}), f2],

    ["zfcg_liubiao_xianji_gg",
     "http://www.lazfcg.cn/CmsNewsController.do?method=newsList&channelCode=zfcg_1130&sign=&parentCode=sjcg&page=1&rp=20&param=bulletin&id=zfcg_1130",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '县级'}), f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="安徽省六安市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "anhui_luan"])
