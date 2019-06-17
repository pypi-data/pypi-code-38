import time

import pandas as pd
import re

from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from zhulong.util.etl import est_tbs, est_meta, est_html, gg_existed, est_gg, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hefei.gov.cn/jyxx/002001/002001002/moreinfo_jyxx.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_ = 'xiaogan'


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="list-paging"]/div')
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text

    cnum = re.findall('(\d+)\/\d+页', txt)[0]

    if int(cnum) != num:
        locator = (By.XPATH, '//div[@class="right-list"]/ul/li/a')
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-30:]

        new_url = re.sub('index[_\d]*', 'index_' + str(num), driver.current_url)
        # print(new_url)
        driver.get(new_url)

        locator = (By.XPATH, '//div[@class="right-list"]/ul/li/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    body = etree.HTML(html)
    content_list = body.xpath('//div[@class="right-list"]/ul/li')
    for content in content_list:
        name = content.xpath("./a/@title")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        href = content.xpath("./a/@href")[0].strip()

        tmp = [name, ggstart_time, href]
        data.append(tmp)
        # print(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="list-paging"]/div')
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text

    total = re.findall('/(\d+)页', txt)[0]
    total = int(total)

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="content-box"]')

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

    soup = BeautifulSoup(page, 'lxml')

    div = soup.find('div', class_='content-box')

    return div


data = [
    #
    ["gcjs_zhaobiao_gg", "http://xgxz.xiaogan.gov.cn/zbgg/index.jhtml", ['name', 'ggstart_time', 'href', 'info'], f1, f2],
    ["gcjs_biangeng_gg", "http://xgxz.xiaogan.gov.cn/bgcqtz/index.jhtml", ['name', 'ggstart_time', 'href', 'info'], f1, f2],
    ["gcjs_gqita_pingbiao_gg", "http://xgxz.xiaogan.gov.cn/pbjggs/index.jhtml", ['name', 'ggstart_time', 'href', 'info'], add_info(f1,{'tag':'评标'}), f2],

    ["gcjs_zhongbiao_gg", "http://xgxz.xiaogan.gov.cn/zbjggg/index.jhtml", ['name', 'ggstart_time', 'href', 'info'], f1, f2],
    ["gcjs_kongzhijia_gg", "http://xgxz.xiaogan.gov.cn/zgxj/index.jhtml", ['name', 'ggstart_time', 'href', 'info'], f1, f2],

    ["zfcg_zhaobiao_gg", "http://xgxz.xiaogan.gov.cn/cggg/index.jhtml", ['name', 'ggstart_time', 'href', 'info'], f1, f2],
    ["zfcg_biangeng_gg", "http://xgxz.xiaogan.gov.cn/bggg/index.jhtml", ['name', 'ggstart_time', 'href', 'info'], f1, f2],
    ["zfcg_gqita_zhong_liu_gg", "http://xgxz.xiaogan.gov.cn/jggg/index.jhtml", ['name', 'ggstart_time', 'href', 'info'], f1, f2],

    ["jqita_gqita_gg", "http://xgxz.xiaogan.gov.cn/qtxm/index.jhtml", ['name', 'ggstart_time', 'href', 'info'], f1, f2],
    ["jqita_gqita_zfcg_gg", "http://xgxz.xiaogan.gov.cn/zfcg/index.jhtml", ['name', 'ggstart_time', 'href', 'info'], add_info(f1,{'tag':'政府采购'}), f2],
    ["jqita_gqita_jsgc_gg", "http://xgxz.xiaogan.gov.cn/jsgc/index.jhtml", ['name', 'ggstart_time', 'href', 'info'], add_info(f1,{'tag':'建设工程'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖北省孝感市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "hubei", "xiaogan"]

    work(conp=conp)
    # driver = webdriver.Chrome()
    # driver.get('http://xgxz.xiaogan.gov.cn/zbgg/index.jhtml')
    # f1(driver, 3)
    # print(f3(driver, 'http://xgxz.xiaogan.gov.cn:80/zbgg/286010.jhtml'))
