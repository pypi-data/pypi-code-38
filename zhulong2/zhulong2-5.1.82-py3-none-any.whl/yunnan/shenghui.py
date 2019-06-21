import random

import pandas as pd
import re

import requests
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

import time

from zhulong2.util.etl import est_html, est_meta, add_info, est_meta_large

from zhulong2.util.fake_useragent import UserAgent

_name_ = "yunnan_shenghui"

tt = None


def f1(driver, num):
    tt_url = 'http://www.yngp.com/bulletin.do?method=moreListQuery'
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies = ''
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': user_agent,
    }
    payloadData = {
        'current': num,
        'rowCount': 10,
        'searchPhrase': '',
        'query_sign': tt,
    }
    # 下载超时
    timeOut = 25
    sesion = requests.session()
    if proxies:
        res = requests.post(url=tt_url, headers=headers, data=payloadData, timeout=timeOut, proxies=proxies)
    else:
        res = sesion.post(url=tt_url, headers=headers, data=payloadData, timeout=timeOut)
    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        html = res.text
        html_data = json.loads(html)
        lis = html_data["rows"]
        data = []
        for tr in lis:
            title = tr['bulletintitle']
            td = tr['beginday']
            info_id = tr['bulletin_id']
            link = 'http://www.yngp.com/newbulletin_zz.do?method=preinsertgomodify&operator_state=1&flag=view&bulletin_id=' + info_id + '&&porid=' + tt + '&t_k=null'
            try:
                leixing = tr['bulletinclasschina']
                diqu = tr['codeName']
                finishday = tr['finishday']
                info = {'lx': '{}'.format(leixing), 'diqu': '{}'.format(diqu), 'ggend_time': '{}'.format(finishday)}
                info = json.dumps(info, ensure_ascii=False)
            except:
                info = None
            tmp = [title, td, link, info]
            data.append(tmp)
        df = pd.DataFrame(data=data)
        return df


def f2(driver):
    global tt
    tt = None
    start_url = driver.current_url
    tt = start_url.rsplit('=', maxsplit=1)[1]
    page_num = get_pageall(tt)
    driver.quit()
    return int(page_num)


def get_pageall(tt):
    tt_url = 'http://www.yngp.com/bulletin.do?method=moreListQuery'
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': user_agent,
    }
    payloadData = {
        'current': 1,
        'rowCount': 10,
        'searchPhrase': '',
        'query_sign': tt,
    }
    # 下载超时
    timeOut = 25
    res = requests.post(url=tt_url, headers=headers, data=payloadData, timeout=timeOut)
    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        html = res.text
        html_data = json.loads(html)
        total = int(html_data['totlePageCount'])
        return total


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='searchPanel'][string-length()>10]")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('div', id='searchPanel')
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "http://www.yngp.com/bulletin.do?method=moreListQuery&key=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_gqita_zhao_zhong_ppp_gg",
     "http://www.yngp.com/bulletin.do?method=moreListQuery&key=4",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': 'ppp合作伙伴采购信息'}), f2],
    # #
    ["zfcg_zhaobiao_danyilaiyuan_gg",
     "http://www.yngp.com/bulletin.do?method=moreListQuery&key=3",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '单一来源'}), f2],
    # #
    ["zfcg_zhaobiao_jkcp_gg",
     "http://www.yngp.com/bulletin.do?method=moreListQuery&key=5",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '进口产品'}), f2],
    # #
    ["zfcg_zhongbiao_gg",
     "http://www.yngp.com/bulletin.do?method=moreListQuery&key=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["zfcg_gqita_bian_zhongz_gg",
     "http://www.yngp.com/bulletin.do?method=moreListQuery&key=7",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="云南省省级", **args)
    est_html(conp, f=f3, **args)


# zfcg_zhaobiao_gg页数太多跑不完
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "yunnan"])
