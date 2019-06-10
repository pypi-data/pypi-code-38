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

_name_ = 'jiangsu_changzhou'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@width='88%']")
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
    div = soup.find('table', width='88%')
    return div


def f1(driver, num):
    locator = (By.XPATH, '//table[@class="Border2"]//tr[1]//a[2]')
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//table[@class="Border2"]//tr[1]//a[2]').get_attribute("href")[-30:]
    try:
        cnum = \
        re.findall(r'(\d+)/', driver.find_element_by_xpath('//meta[@name="description"]').getattribute("content").text)[
            0]
    except:
        cnum = 1
    # print('val', val, 'cnum', cnum)
    if int(cnum) != int(num):
        url = driver.current_url
        url = re.sub(r'index[_\d]*', 'index_' + str(num), url)
        driver.get(url)
        locator = (By.XPATH, '//table[@class="Border2"]//tr[1]//a[2][not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@class="Border2"]//tr')
    for content in content_list:
        name = content.xpath("./td/a[2]/text()")[0].strip()
        ggstart_time = content.xpath('./td[last()]/text()')[0].strip()
        href = content.xpath("./td/a[2]/@href")[0].strip()
        temp = [name, ggstart_time, href]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//meta[@name="description"]')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    try:
        total_page = \
        re.findall(r'/(\d+)', driver.find_element_by_xpath('//meta[@name="description"]').get_attribute("content"))[0]
    except:
        total_page = 1
    # print('total_page', total_page)
    driver.quit()
    return int(total_page)


data = [
    #
    ["zfcg_zhaobiao_bumen_gg", "http://zfcg.changzhou.gov.cn/html/ns/bmcg_cggg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':"部门"}), f2],
    ["zfcg_biangeng_bumen_gg", "http://zfcg.changzhou.gov.cn/html/ns/bmcg_gzgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':"部门"}), f2],
    ["zfcg_yucai_bumen_gg", "http://zfcg.changzhou.gov.cn/html/ns/bmcg_cgyg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':"部门"}), f2],
    ["zfcg_zhongbiao_bumen_gg", "http://zfcg.changzhou.gov.cn/html/ns/bmcg_cjgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':"部门"}), f2],
    ["zfcg_zhaobiao_fangshigongshi_bumen_gg", "http://zfcg.changzhou.gov.cn/html/ns/bmcg_fsgs/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':"部门",'tag2':"方式公示"}), f2],

    ["zfcg_zhaobiao_jizhong_gg", "http://zfcg.changzhou.gov.cn/html/ns/zfjzcg_cggg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':"集中"}), f2],
    ["zfcg_biangeng_jizhong_gg", "http://zfcg.changzhou.gov.cn/html/ns/zfjzcg_gzgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':"集中"}), f2],
    ["zfcg_zhongbiao_jizhong_gg", "http://zfcg.changzhou.gov.cn/html/ns/zfjzcg_cjgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':"集中"}), f2],
    ["zfcg_yucai_jizhong_gg", "http://zfcg.changzhou.gov.cn/html/ns/zfjzcg_cgyg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':"集中"}), f2],
    ["zfcg_zhaobiao_fangshigongshi_jizhong_gg", "http://zfcg.changzhou.gov.cn/html/ns/zfjzcg_fsgs/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':"集中",'tag2':"方式公示"}), f2],

    ["zfcg_zhaobiao_daili_gg", "http://zfcg.changzhou.gov.cn/html/ns/dlcg_cggg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':"代理采购"}), f2],
    ["zfcg_biangeng_daili_gg", "http://zfcg.changzhou.gov.cn/html/ns/dlcg_gzgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':"代理采购"}), f2],
    ["zfcg_zhongbiao_daili_gg", "http://zfcg.changzhou.gov.cn/html/ns/dlcg_cjgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':"代理采购"}), f2],
    ["zfcg_yucai_daili_gg", "http://zfcg.changzhou.gov.cn/html/ns/dlcg_cgyg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':"代理采购"}), f2],
    ["zfcg_zhaobiao_fangshigongshi_daili_gg", "http://zfcg.changzhou.gov.cn/html/ns/dlcg_cgyg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':"代理采购",'tag2':"方式公示"}), f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="江苏省常州市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "jiangsu_changzhou"])
