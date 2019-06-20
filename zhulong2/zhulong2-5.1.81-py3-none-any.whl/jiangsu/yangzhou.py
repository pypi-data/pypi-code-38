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

_name_ = 'jiangsu_yangzhou'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='contentShow']")
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
    div = soup.find('div', class_='contentShow')
    return div


def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="item lh jt_dott f14"]')
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//ul[@class="item lh jt_dott f14"]/li[1]/a').get_attribute("href")[-40:]
    if "channel_id" not in driver.current_url:

        cnum = re.findall('第 (\d+) 页', driver.find_element_by_xpath('//div[@class="pagination_index_last"]').text)[0]
    else:
        cnum = driver.find_element_by_xpath('//input[@id="currentPage"]').get_attribute('value')
    # print('val', val, 'cnum', cnum)
    if int(cnum) != int(num):
        url = driver.current_url
        if "channel_id" not in url:
            if num != "1":
                url = re.sub(r'[\d_]*\.shtml', '_' + str(num) + ".shtml", url, count=1)
            else:
                url = re.sub(r'[\d_]*\.shtml', ".shtml", url, count=1)
        else:
            url = re.sub(r'currentPage=[\d]+', 'currentPage=' + str(num), url, count=1)

        driver.get(url)
        locator = (By.XPATH, '//ul[@class="item lh jt_dott f14"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
    data = []
    url = driver.current_url
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@class="item lh jt_dott f14"]/li')
    for content in content_list:
        try:
            name = content.xpath("./a/text()")[0].strip()
        except:
            name = content.xpath("./a/span/text()")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        if "channel_id" not in url:
            href = "http://zfcg.yangzhou.gov.cn" + content.xpath("./a/@href")[0]
        else:
            href = content.xpath("./a/@href")[0]
        temp = [name, ggstart_time, href]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    if "qtyy" in driver.current_url:
        locator = (By.XPATH, "//input[@id='currentPage']/parent::span")
        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
        total_page = \
            re.findall('共 (\d+) 页', driver.find_element_by_xpath("//input[@id='currentPage']/parent::span").text)[0]
    else:
        locator = (By.XPATH, '//div[@class="pagination_index_last"]')
        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
        total_page = \
        re.findall('共 (\d+) 页', driver.find_element_by_xpath('//div[@class="pagination_index_last"]').text)[0]
    driver.quit()
    return int(total_page)


data = [
    #
    ["zfcg_zhaobiao_gongkai_gg", "http://zfcg.yangzhou.gov.cn/zfcgw/gkzb/list.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'公开'}), f2],
    ["zfcg_zhaobiao_cuoshang_gg", "http://zfcg.yangzhou.gov.cn/zfcgw/jzxcs/list.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'磋商'}), f2],
    ["zfcg_zhaobiao_danyilaiyuan_gg", "http://zfcg.yangzhou.gov.cn/zfcgw/dyly/list.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'单一来源'}), f2],
    ["zfcg_zhaobiao_tanpan_gg", "http://zfcg.yangzhou.gov.cn/zfcgw/jzxtp/list.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'谈判'}), f2],
    ["zfcg_zhaobiao_xunjia_gg", "http://zfcg.yangzhou.gov.cn/zfcgw/xjcg/list.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'询价'}), f2],

    ["zfcg_zhongbiao_gongkai_gg", "http://zfcg.yangzhou.gov.cn/zfcgw/gkzbi/list.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'公开'}), f2],
    ["zfcg_zhongbiao_cuoshang_gg", "http://zfcg.yangzhou.gov.cn/zfcgw/cjjzxcs/list.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'磋商'}), f2],
    ["zfcg_zhongbiao_danyilaiyuan_gg", "http://zfcg.yangzhou.gov.cn/zfcgw/dylyi/list.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'单一来源'}), f2],
    ["zfcg_zhongbiao_tanpan_gg", "http://zfcg.yangzhou.gov.cn/zfcgw/jzxtpi/list.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'谈判'}), f2],
    ["zfcg_zhongbiao_xunjia_gg", "http://zfcg.yangzhou.gov.cn/zfcgw/xjcgi/list.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'询价'}), f2],

    ["zfcg_zhaobiao_xianqu_gg",
     "http://zfcg.yangzhou.gov.cn/qtyy/zfcgw/xsq_list.jsp?currentPage=1&channel_id=4749b63313a040b7bd17119f43f19307",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'县区'}), f2],
    ["zfcg_zhongbiao_xianqu_gg",
     "http://zfcg.yangzhou.gov.cn/qtyy/zfcgw/xsq_list.jsp?currentPage=1&channel_id=781558110dac4d5a96083bb1bd49d0a3",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'县区'}), f2],

    ["zfcg_zhaobiao_bumenshehui_gg",
     "http://zfcg.yangzhou.gov.cn/qtyy/zfcgw/bmsh_list.jsp?currentPage=1&channel_id=4bacf5f80b94422c8c844353f34ea331",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'部门集中采购、社会代理机构采购信息'}), f2],
    ["zfcg_zhongbiao_bumenshehui_gg",
     "http://zfcg.yangzhou.gov.cn/qtyy/zfcgw/bmsh_list.jsp?currentPage=1&channel_id=fdb15181069042f5b9b216bb48798f6b",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'部门集中采购、社会代理机构采购信息','tag1':'结果'}), f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="江苏省扬州市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "jiangsu_yangzhou"])
