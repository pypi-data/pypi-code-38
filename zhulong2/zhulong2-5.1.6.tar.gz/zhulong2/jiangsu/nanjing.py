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

_name_ = 'jiangsu_nanjing'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='content']")
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
    div = soup.find('div', class_='content')
    return div


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='R_cont_detail']/ul/li[1]/a")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//div[@class='R_cont_detail']/ul/li[1]/a").get_attribute("href")[-40:]

    cnum = re.findall(r'(\d*)\.', driver.current_url)[-1]
    if cnum == '':
        cnum = 1
    # print('val', val, 'cnum', cnum)
    if int(cnum) != int(num):
        url = driver.current_url
        url = re.sub(r'index[\d_]*', 'index_' + str(num - 1), url, count=1)
        # print("url",url)
        driver.get(url)
        locator = (By.XPATH, '//div[@class="R_cont_detail"]/ul/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
    data = []
    url = driver.current_url.rsplit('/', maxsplit=1)[0]
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@class='R_cont_detail']/ul/li")
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
    locator = (By.XPATH, "//div[@class='page_turn']")
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    try:
        total_page = re.findall('有 (\d+) 页', driver.find_element_by_xpath("//div[@class='page_turn']").text)[0]
    except:
        total_page = 1
    # print('total_page', total_page)
    driver.quit()
    return int(total_page)


data = [
    #
    ["zfcg_zhaobiao_jizhong_gg", "http://www.njgp.gov.cn/cgxx/cggg/jzcgjg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'集中'}), f2],
    ["zfcg_zhaobiao_bumenjizhong_gg", "http://www.njgp.gov.cn/cgxx/cggg/bmjzcgjg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'部门集中'}), f2],
    ["zfcg_zhaobiao_quji_gg", "http://www.njgp.gov.cn/cgxx/cggg/qjcgjg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'区级'}), f2],
    ["zfcg_zhaobiao_shehui_gg", "http://www.njgp.gov.cn/cgxx/cggg/shdljg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'社会'}), f2],
    ["zfcg_zhaobiao_gqita_gg", "http://www.njgp.gov.cn/cgxx/cggg/qtbx/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'其他'}), f2],

    ["zfcg_biangeng_gg", "http://www.njgp.gov.cn/cgxx/gzgg/index.html", ["name", "ggstart_time", "href", "info"], f1,
     f2],
    ["zfcg_biangeng_caigoufangshi_gg", "http://www.njgp.gov.cn/cgxx/cgfsbg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'采购方式'}), f2],
    ["zfcg_zhongbiao_gg", "http://www.njgp.gov.cn/cgxx/cgcjjg/index.html", ["name", "ggstart_time", "href", "info"], f1,
     f2],
    ["zfcg_liubiao_gg", "http://www.njgp.gov.cn/cgxx/zzgg/index.html", ["name", "ggstart_time", "href", "info"], f1,
     f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="江苏省南京市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "jiangsu_nanjing"])
