import json
import math
import pandas as pd
import re

import requests
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

_name_ = 'zhejiang_shenghui'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='gpoz-detail-content'][string-length()>10]")
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
    div = soup.find('div', class_='gpoz-detail-content')
    return div


def f1(driver, num):
    data1 = []
    new_url = re.sub(r'pageNo=\d+', 'pageNo=' + str(num), driver.current_url)
    page_html = requests.get(new_url).content.decode('utf-8')
    page_json = json.loads(page_html)
    content_list = page_json["articles"]
    for content in content_list:
        name = content["title"] + '[' + content["projectCode"] + ']'
        ggstart_time = time.strftime('%Y-%m-%d', time.localtime(int(content['pubDate']) // 1000))
        href = content['url']
        area_info = content['districtName']
        info = json.dumps({'area':area_info},ensure_ascii=False)
        temp = [name, ggstart_time, href, info]
        # print(temp)
        data1.append(temp)
    df = pd.DataFrame(data=data1)
    return df


def f2(driver):
    page_html = requests.get(driver.current_url).content.decode('utf-8')
    page_json = json.loads(page_html)
    page_temp = math.ceil(int(page_json["realCount"]) / int(page_json['pageSize']))
    if page_temp > 100:
        total_page = 100
    else:
        total_page = page_temp
    driver.quit()
    return int(total_page)


data = [
    # #
    ["zfcg_zhaobiao_danyilaiyuan_gg",
     "http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=100&pageNo=1&sourceAnnouncementType=3012&url=http%3A%2F%2Fnotice.zcy.gov.cn%2Fnew%2FnoticeSearch",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'单一来源'}), f2],
    ["zfcg_zhaobiao_gongkai_gg",
     "http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=100&pageNo=1&sourceAnnouncementType=3001&url=http%3A%2F%2Fnotice.zcy.gov.cn%2Fnew%2FnoticeSearch",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'公开'}), f2],
    ["zfcg_zhaobiao_tanpan_gg",
     "http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=100&pageNo=1&sourceAnnouncementType=3002&url=http%3A%2F%2Fnotice.zcy.gov.cn%2Fnew%2FnoticeSearch",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'谈判'}), f2],
    ["zfcg_zhaobiao_xunjia_gg",
     "http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=100&pageNo=1&sourceAnnouncementType=3003&url=http%3A%2F%2Fnotice.zcy.gov.cn%2Fnew%2FnoticeSearch",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'询价'}), f2],
    ["zfcg_zgys_yaoqing_gg",
     "http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=100&pageNo=1&sourceAnnouncementType=3008&url=http%3A%2F%2Fnotice.zcy.gov.cn%2Fnew%2FnoticeSearch",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'邀请'}), f2],
    ["zfcg_zgys_gongkai_gg",
     "http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=100&pageNo=1&sourceAnnouncementType=2001&url=http%3A%2F%2Fnotice.zcy.gov.cn%2Fnew%2FnoticeSearch",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'公开'}), f2],
    ["zfcg_zhaobiao_cuoshang_gg",
     "http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=100&pageNo=1&sourceAnnouncementType=3011&url=http%3A%2F%2Fnotice.zcy.gov.cn%2Fnew%2FnoticeSearch",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'磋商'}), f2],
    ["zfcg_zhaobiao_qita_gg",
     "http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=100&pageNo=1&sourceAnnouncementType=2002&url=http%3A%2F%2Fnotice.zcy.gov.cn%2Fnew%2FnoticeSearch",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'其他'}), f2],

    ["zfcg_zhaobiao_qitafeizhengfu_gg",
     "http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=100&pageNo=1&url=http%3A%2F%2Fnotice.zcy.gov.cn%2Fnew%2FnoticeSearch&sourceAnnouncementType=10007",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'其他非政府'}), f2],
    ["zfcg_zhaobiao_qita2_gg",
     "http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=100&pageNo=1&sourceAnnouncementType=4007&url=http%3A%2F%2Fnotice.zcy.gov.cn%2Fnew%2FnoticeSearch",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'其他'}), f2],

    ["zfcg_yucai_gg",
     "http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=100&pageNo=1&sourceAnnouncementType=3014&url=http%3A%2F%2Fnotice.zcy.gov.cn%2Fnew%2FnoticeSearch",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=100&pageNo=1&sourceAnnouncementType=3005&url=http%3A%2F%2Fnotice.zcy.gov.cn%2Fnew%2FnoticeSearch",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_qita_gg",
     "http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=100&pageNo=1&sourceAnnouncementType=3019&url=http%3A%2F%2Fnotice.zcy.gov.cn%2Fnew%2FnoticeSearch",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'其他'}), f2],
    ["zfcg_biangeng_feizhengfu_gg",
     "http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=15&pageNo=1&sourceAnnouncementType=10003&url=http%3A%2F%2Fnotice.zcy.gov.cn%2Fnew%2FnoticeSearch",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'非政府'}), f2],
    ["zfcg_biangeng_qitafeizhengfu_gg",
     "http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=100&pageNo=1&url=http%3A%2F%2Fnotice.zcy.gov.cn%2Fnew%2FnoticeSearch&sourceAnnouncementType=10008",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'其他非政府'}), f2],

    ["zfcg_zhongbiao_gg",
     "http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=100&pageNo=1&sourceAnnouncementType=3004&url=http%3A%2F%2Fnotice.zcy.gov.cn%2Fnew%2FnoticeSearch",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_feizhengfu_gg",
     "http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=100&pageNo=1&url=http%3A%2F%2Fnotice.zcy.gov.cn%2Fnew%2FnoticeSearch&sourceAnnouncementType=10011",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'非政府'}), f2],
    ["zfcg_zhongbiao_qitafeizhengfu_gg",
     "http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=100&pageNo=1&url=http%3A%2F%2Fnotice.zcy.gov.cn%2Fnew%2FnoticeSearch&sourceAnnouncementType=10009",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'其他非政府'}), f2],

    ["zfcg_liubiao_gg",
     "http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=100&pageNo=1&sourceAnnouncementType=3007&url=http%3A%2F%2Fnotice.zcy.gov.cn%2Fnew%2FnoticeSearch",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_gqita_liu_zhongz_gg",
     "http://manager.zjzfcg.gov.cn/cms/api/cors/getRemoteResults?pageSize=100&pageNo=1&sourceAnnouncementType=3015&url=http%3A%2F%2Fnotice.zcy.gov.cn%2Fnew%2FnoticeSearch",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="浙江省", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "zhejiang"],headless=False)
