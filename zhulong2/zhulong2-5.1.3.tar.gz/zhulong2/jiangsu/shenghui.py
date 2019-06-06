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

_name_ = 'jiangsu_shenghui'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='detail']")
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
    div = soup.find('div', class_='detail')
    return div


def f1(driver, num):
    locator = (By.XPATH, "//div[@id='newsList' or @class='list_list']/ul/li[1]/a")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//div[@id='newsList' or @class='list_list']/ul/li[1]/a").get_attribute("href")[
          -40:]

    cnum = re.findall(r'(\d*)\.', driver.current_url)[-1]
    if cnum == '':
        cnum = 1
    if int(cnum) != int(num):
        url = driver.current_url
        url = re.sub(r'index[\d_]*', 'index_' + str(num - 1), url, count=1)
        driver.get(url)
        locator = (By.XPATH, '//div[@id="newsList" or @class="list_list"]/ul/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
    data = []
    url = driver.current_url.rsplit('/', maxsplit=1)[0]
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@id='newsList' or @class='list_list']/ul/li")
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        ggstart_time = content.xpath('./text()')[1].strip()
        href = url + content.xpath("./a/@href")[0].strip('.')
        temp = [name, ggstart_time, href]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='digg']")
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    try:
        total_page = re.findall('有 (\d+) 页', driver.find_element_by_xpath("//div[@class='digg']/div").text)[0]
    except:
        total_page = 1
    driver.quit()
    return int(total_page)


data = [
    # #
    ["zfcg_zhaobiao_old_gg", "http://www.ccgp-jiangsu.gov.cn/cgxx/cggg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'旧'}), f2],
    ["zfcg_yucai_old_gg", "http://www.ccgp-jiangsu.gov.cn/cgxx/cgyg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'旧'}), f2],
    ["zfcg_biangeng_old_gg", "http://www.ccgp-jiangsu.gov.cn/cgxx/gzgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'旧'}), f2],
    ["zfcg_zhongbiao_old_gg", "http://www.ccgp-jiangsu.gov.cn/cgxx/cjgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'旧'}), f2],
    ["zfcg_yanshou_old_gg", "http://www.ccgp-jiangsu.gov.cn/cgxx/ysgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'旧'}), f2],

    ["zfcg_zgys_new_gg", "http://www.ccgp-jiangsu.gov.cn/ggxx/zgysgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'新'}), f2],
    ["zfcg_zhaobiao_gongkai_new_gg", "http://www.ccgp-jiangsu.gov.cn/ggxx/gkzbgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'新','method':'公开'}), f2],
    ["zfcg_zhaobiao_yaoqing_new_gg", "http://www.ccgp-jiangsu.gov.cn/ggxx/yqzbgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'新','method':'邀请'}), f2],
    ["zfcg_zhaobiao_tanpan_new_gg", "http://www.ccgp-jiangsu.gov.cn/ggxx/jztbgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'新','method':'谈判'}), f2],
    ["zfcg_zhaobiao_cuoshang_new_gg", "http://www.ccgp-jiangsu.gov.cn/ggxx/jzqsgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'新','method':'磋商'}), f2],
    ["zfcg_zhaobiao_danyilaiyuan_new_gg", "http://www.ccgp-jiangsu.gov.cn/ggxx/dylygg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'新','method':'单一来源'}), f2],
    ["zfcg_zhaobiao_xunjia_new_gg", "http://www.ccgp-jiangsu.gov.cn/ggxx/xjgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'新','method':'询价'}), f2],
    ["zfcg_zhongbiao_new_gg", "http://www.ccgp-jiangsu.gov.cn/ggxx/zbgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'新'}), f2],

    # ["zfcg_zhongbiao_new_gg","http://www.ccgp-jiangsu.gov.cn/ggxx/zbgg/index.html",["name", "ggstart_time", "href", "info"], f1, f2],
    # ["zfcg_chengjiao_new_gg","http://www.ccgp-jiangsu.gov.cn/ggxx/cgcjgg/index.html",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_chengjiao_new_gg", "http://www.ccgp-jiangsu.gov.cn/ggxx/cgcjgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'新'}), f2],
    ["zfcg_liubiao_new_gg", "http://www.ccgp-jiangsu.gov.cn/ggxx/zzgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'新'}), f2],
    ["zfcg_biangeng_new_gg", "http://www.ccgp-jiangsu.gov.cn/ggxx/cggzgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'新'}), f2],
    ["zfcg_gqita_new_gg", "http://www.ccgp-jiangsu.gov.cn/ggxx/qtgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'新'}), f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="江苏省", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "jiangsu"])
