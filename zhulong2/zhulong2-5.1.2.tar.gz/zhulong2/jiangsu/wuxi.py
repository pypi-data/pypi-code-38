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

_name_ = 'jiangsu_wuxi'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='sch_box']")
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
    div = soup.find('div', id='sch_box')
    return div


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="Main_List"]//li/a | //*[@id="sch_box"]/div/li[1]/a')
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath(
        '//div[@class="Main_List"]/ul[1]/li[1]/a | //*[@id="sch_box"]/div/li[1]/a').get_attribute("href")[-12:]
    try:
        cnum = re.findall('(\d+)/', driver.find_element_by_xpath('//div[@class="pageNum"]/p/span[1]').text)[0]
    except:
        cnum = driver.find_element_by_xpath('//span[@class="page current"]').text
    url = driver.current_url
    # print('val', val, 'cnum', cnum)
    if int(cnum) != int(num):
        if "loadData" in driver.page_source:
            driver.execute_script("dataSeD.loadData(%s)" % num)
        else:
            to_url = re.sub(r'page=\d+', 'page=' + str(num), url)
            # print(to_url)
            driver.get(to_url)
        locator = (By.XPATH,
                   '//div[@class="Main_List"]/ul[1]/li[1]/a[not(contains(@href,"%s"))] | //*[@id="sch_box"]/div/li[1]/a[not(contains(@href,"%s"))]' % (
                   val, val))
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="Main_List"]//li | //*[@id="sch_box"]/div/li')
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        ggstart_time = content.xpath('./span/text()')[0].strip().strip('(').strip(')')
        if "http://" not in content.xpath("./a/@href")[0]:
            if "inform" in driver.current_url:
                href = "http://dzhcg.sinopr.org" + content.xpath("./a/@href")[0]
            else:
                href = "http://cz.wuxi.gov.cn" + content.xpath("./a/@href")[0]
        else:
            href = content.xpath("./a/@href")[0]
        temp = [name, ggstart_time, href]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    if "inform" in driver.current_url:
        val = driver.find_element_by_xpath('//*[@id="sch_box"]/div/li[1]/a').get_attribute("href")[-10:]
        driver.find_element_by_xpath("//span[@class='last']").click()
        locator = (By.XPATH, '//*[@id="sch_box"]/div/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
        total_page = driver.find_element_by_xpath('//span[@class="page current"]').text.strip()
    else:
        locator = (By.XPATH, '//div[@class="pageNum"]/p/span[1]')
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
        total_page = re.findall('/(\d+)', driver.find_element_by_xpath('//div[@class="pageNum"]/p/span[1]').text)[0]

    # print('total_page', total_page)
    driver.quit()
    return int(total_page)


data = [
    ["zfcg_zhaobiao_gg", "http://cz.wuxi.gov.cn/ztzl/zfcg/cgxxgg/cggg/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg", "http://cz.wuxi.gov.cn/ztzl/zfcg/cgxxgg/gzgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_yucai_gg", "http://cz.wuxi.gov.cn/ztzl/zfcg/cgxxgg/cgyg/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    # 出现弹窗，但是没有出现数据。
    # ["zfcg_biangeng_fangshi_gg", "http://cz.wuxi.gov.cn/ztzl/zfcg/cgxxgg/cgfsbggg/index.shtml",
    #  ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'方式'}), f2],
    ["zfcg_zhongbiao_gg", "http://cz.wuxi.gov.cn/ztzl/zfcg/cgxxgg/cjgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_xuqiu_gg", "http://dzhcg.sinopr.org/informs/cgxxgg.html?page=1&type=3",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'区县'}), f2],
    ["zfcg_yanshou_gg", "http://dzhcg.sinopr.org/informs/cgxxgg.html?page=1&type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="江苏省无锡市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "jiangsu_wuxi"])
