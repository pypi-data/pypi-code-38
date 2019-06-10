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
from zhulong2.util.etl import est_html, est_meta, add_info


_name_ = "hainan_wenchang"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='nei02_04_01']/ul/li[1]/em/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//select[@name='currentPage']/option[@selected='selected']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(st)
    except:
        cnum = 1
    url = driver.current_url
    if num != cnum:
        val = driver.find_element_by_xpath("//div[@class='nei02_04_01']/ul/li[1]/em/a").get_attribute('href')[-20:]
        selector = Select(driver.find_element_by_xpath("//select[@name='currentPage']"))
        selector.select_by_value('{}'.format(num))

        locator = (By.XPATH, "//div[@class='nei02_04_01']/ul/li[1]/em/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("div", class_='nei02_04_01')
    ul = div.find("ul")
    lis = ul.find_all('li')
    data = []
    for tr in lis:
        a = tr.find('em').a
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        td = tr.find('i').text.strip()
        link = a['href'].strip()
        if "http" in link:
            link = link
        else:
            link = 'http://www.ccgp-hainan.gov.cn' + link
        info = {}
        if tr.find('b').a:
            b = tr.find('b').a.text.strip()
            if b:info['diqu'] = b
        if tr.find('tt').a:
            tt = tr.find('tt').a.text.strip()
            if tt:info['lx'] = tt
        if info:info = json.dumps(info, ensure_ascii=False)
        else:info = None
        tmp = [title, td, link, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='nei02_04_01']/ul/li[1]/em/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//select[@name='currentPage']/option[last()]")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = int(st)
    driver.quit()
    return num


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='nei03_02'][string-length()>10] | //div[@class='cen-main'][string-length()>10]")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('div', class_='nei03_02')
    if div == None:
        div = soup.find('div', class_='cen-main')
    return div


data = [
    # #
    ["zfcg_zgys_gg",
     "http://www.ccgp-hainan.gov.cn/cgw/cgw_list.jsp?bid_type=100&zone=%E6%96%87%E6%98%8C%E5%B8%82",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["zfcg_zhaobiao_gongkai_gg",
     "http://www.ccgp-hainan.gov.cn/cgw/cgw_list.jsp?bid_type=101&zone=%E6%96%87%E6%98%8C%E5%B8%82",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'公开招标'}), f2],
    # #
    ["zfcg_zhaobiao_xunjia_gg",
     "http://www.ccgp-hainan.gov.cn/cgw/cgw_list.jsp?bid_type=102&zone=%E6%96%87%E6%98%8C%E5%B8%82",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'询价招标'}), f2],
    # #
    ["zfcg_zhaobiao_tanpan_gg",
     "http://www.ccgp-hainan.gov.cn/cgw/cgw_list.jsp?bid_type=103&zone=%E6%96%87%E6%98%8C%E5%B8%82",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'竞争性谈判'}), f2],
    # #
    ["zfcg_zhaobiao_cuoshang_gg",
     "http://www.ccgp-hainan.gov.cn/cgw/cgw_list.jsp?bid_type=1031&zone=%E6%96%87%E6%98%8C%E5%B8%82",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'竞争性磋商'}), f2],
    # #
    ["zfcg_zhaobiao_danyilaiyuan_gg",
     "http://www.ccgp-hainan.gov.cn/cgw/cgw_list.jsp?bid_type=104&zone=%E6%96%87%E6%98%8C%E5%B8%82",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'单一来源'}), f2],
    # #
    ["zfcg_zhaobiao_yaoqing_gg",
     "http://www.ccgp-hainan.gov.cn/cgw/cgw_list.jsp?bid_type=105&zone=%E6%96%87%E6%98%8C%E5%B8%82",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'邀请招标'}), f2],
    # #
    ["zfcg_gqita_gg",
     "http://www.ccgp-hainan.gov.cn/cgw/cgw_list.jsp?bid_type=107&zone=%E6%96%87%E6%98%8C%E5%B8%82",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["zfcg_zhongbiao_gg",
     "http://www.ccgp-hainan.gov.cn/cgw/cgw_list.jsp?bid_type=108&zone=%E6%96%87%E6%98%8C%E5%B8%82",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["zfcg_zhongbiao_lx1_gg",
     "http://www.ccgp-hainan.gov.cn/cgw/cgw_list.jsp?bid_type=112&zone=%E6%96%87%E6%98%8C%E5%B8%82",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gglx':'成交公告'}), f2],
    # #
    ["zfcg_liubiao_gg",
     "http://www.ccgp-hainan.gov.cn/cgw/cgw_list.jsp?bid_type=113&zone=%E6%96%87%E6%98%8C%E5%B8%82",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["zfcg_biangeng_gg",
     "http://www.ccgp-hainan.gov.cn/cgw/cgw_list.jsp?bid_type=110&zone=%E6%96%87%E6%98%8C%E5%B8%82",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["zfcg_yucai_gg",
     "http://www.ccgp-hainan.gov.cn/cgw/cgw_list.jsp?bid_type=300&zone=%E6%96%87%E6%98%8C%E5%B8%82",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="海南省文昌市", **args)
    est_html(conp, f=f3, **args)


# 域名变更
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.4.175", "zfcg", "hainan_wenchang"])
    #
