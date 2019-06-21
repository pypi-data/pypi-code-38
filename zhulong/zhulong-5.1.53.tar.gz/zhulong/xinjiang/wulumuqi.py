import json
import time

import pandas as pd
import re

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


_name_ = 'wulumuqi'


def f1(driver, num):
    locator = (By.XPATH, '//table[@id="packTable"]//tr[2]/td[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//nobr[@id="packTableRowCount"]').text.strip()
    cnum = re.findall('显示(.+)到', cnum)[0]
    cnum = int(cnum) // 15 + 1

    if int(cnum) != num:

        val = driver.find_element_by_xpath('//table[@id="packTable"]//tr[2]/td[1]/a').get_attribute('onclick')[-34:-2]

        driver.execute_script("TabAjaxQuery.gotoPage({},'packTable');".format(num))

        locator = (By.XPATH, '//table[@id="packTable"]//tr[2]/td[1]/a[not(contains(@onclick,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lis = soup.find('table', id='packTable').find_all('tr')

    for i in range(1, len(lis)):
        li = lis[i]

        tds = li.find_all('td')
        href = tds[0].a['onclick']
        href = re.findall("this,\'(.+)\'", href)[0]
        name = tds[0].a['title']
        ggstart_time = tds[1].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://ggzy.wlmq.gov.cn/infopublish.do?method=infoPublishView&infoid=' + href

        tmp = [name,  ggstart_time,href]

        data.append(tmp)
        # print(data)
    df = pd.DataFrame(data=data)
    df['info']=None

    return df


def f2(driver):
    locator = (By.XPATH, '//table[@id="packTable"]//tr[2]/td[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('//span[@id="packTablePageCount"]').text

    total = re.findall('/(\d+)', page)[0]
    total = int(total)

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="w_content_main"]')

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

    div = soup.find('div',class_="w_content_main")

    return div


data = [

    ["gcjs_zgys_gg", "http://ggzy.wlmq.gov.cn/generalpage.do?method=showList&fileType=201605-041&faname=201605-038&num=2", ['name', 'ggstart_time', 'href', 'info'],f1, f2],
    ["gcjs_zgysjg_gg", "http://ggzy.wlmq.gov.cn/generalpage.do?method=showList&fileType=201605-042&faname=201605-038&num=3", ['name', 'ggstart_time', 'href', 'info'],f1, f2],
    ["gcjs_zhaobiao_gg", "http://ggzy.wlmq.gov.cn/generalpage.do?method=showList&fileType=201605-043&faname=201605-038&num=4", ['name', 'ggstart_time', 'href', 'info'],f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://ggzy.wlmq.gov.cn/generalpage.do?method=showList&fileType=201605-044&faname=201605-038&num=5", ['name', 'ggstart_time', 'href', 'info'],f1, f2],
    ["gcjs_zhongbiao_gg", "http://ggzy.wlmq.gov.cn/generalpage.do?method=showList&fileType=201605-045&faname=201605-038&num=6", ['name', 'ggstart_time', 'href', 'info'],f1, f2],
    ["gcjs_gqita_gg", "http://ggzy.wlmq.gov.cn/generalpage.do?method=showList&fileType=201807-002&faname=201605-038&num=7", ['name', 'ggstart_time', 'href', 'info'],f1, f2],


    ["zfcg_zhaobiao_gg", "http://ggzy.wlmq.gov.cn/generalpage.do?method=showList&fileType=201605-048&faname=201605-046&num=1", ['name', 'ggstart_time', 'href', 'info'],f1, f2],
    ["zfcg_zhongbiaohx_gg", "http://ggzy.wlmq.gov.cn/generalpage.do?method=showList&fileType=201605-049&faname=201605-046&num=2", ['name', 'ggstart_time', 'href', 'info'],f1, f2],
    ["zfcg_zhongbiao_gg", "http://ggzy.wlmq.gov.cn/generalpage.do?method=showList&fileType=201605-050&faname=201605-046&num=3", ['name', 'ggstart_time', 'href', 'info'],f1, f2],

    ["zfcg_gqita_yanqi_gg", "http://ggzy.wlmq.gov.cn/generalpage.do?method=showList&fileType=201605-051&faname=201605-046&num=4", ['name', 'ggstart_time', 'href', 'info'],add_info(f1,{"tag":"延期公告"}), f2],
    ["zfcg_biangeng_gg", "http://ggzy.wlmq.gov.cn/generalpage.do?method=showList&fileType=201605-052&faname=201605-046&num=5", ['name', 'ggstart_time', 'href', 'info'],f1, f2],
    ["zfcg_liubiao_gg", "http://ggzy.wlmq.gov.cn/generalpage.do?method=showList&fileType=201605-053&faname=201605-046&num=6", ['name', 'ggstart_time', 'href', 'info'],f1, f2],

    ["zfcg_zhaobiao_xieyicaigou_gg", "http://ggzy.wlmq.gov.cn/generalpage.do?method=showList&fileType=201605-095&faname=201605-046&num=7", ['name', 'ggstart_time', 'href', 'info'],add_info(f1,{"zbfs":"协议采购"}), f2],
    ["zfcg_zhaobiao_danyilaiyuan_gg", "http://ggzy.wlmq.gov.cn/generalpage.do?method=showList&fileType=201605-047&faname=201605-046&num=8", ['name', 'ggstart_time', 'href', 'info'],add_info(f1,{"zbfs":"单一来源"}), f2],
    ["zfcg_gqita_ercizhaobiao_gg", "http://ggzy.wlmq.gov.cn/generalpage.do?method=showList&fileType=201807-001&faname=201605-046&num=9", ['name', 'ggstart_time', 'href', 'info'],add_info(f1,{"tag":"二次招标公告"}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="新疆省乌鲁木齐", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "xinjiang", "wulumuqi"]

    work(conp=conp,headless=False,num=1)