import pandas as pd
import re

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

from zhulong3.util.etl import est_html, est_meta, add_info

_name_ = "xinjiang_shenghui"


def f1(driver, num):
    locator = (By.XPATH, "//table[@id='MoreInfoList1_DataGrid1']/tbody/tr[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    locator = (By.XPATH, "//td[@class='yahei redfont']")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@id='MoreInfoList1_DataGrid1']/tbody/tr[1]//a").get_attribute('href')[-30:]
        if 'Paging' not in url:
            s = '&Paging=%d' % (num) if num > 1 else "&Paging=1"
            url = url + s
        if num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
            # print(cnum)
        driver.get(url)
        locator = (By.XPATH, "//table[@id='MoreInfoList1_DataGrid1']/tbody/tr[1]//a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("table", id='MoreInfoList1_DataGrid1').tbody
    lis = div.find_all("tr")
    data = []
    for li in lis:
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        span = li.find_all("td")[-1].text.strip()
        span = re.findall(r'\[(.*)\]', span)[0]
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://ztb.xjjs.gov.cn' + link
        try:
            if li.find('font', color="#FF0000"):
                diqu = li.find('font', color="#FF0000").text.strip()
                diqu = re.findall(r'\[(.*)\]', diqu)[0]
                info = json.dumps({'diqu': diqu}, ensure_ascii=False)
            elif li.find('font', color="#EA481A"):
                diqu = li.find('font', color="#EA481A").text.strip()
                diqu = re.findall(r'\[(.*)\]', diqu)[0]
                info = json.dumps({'diqu': diqu}, ensure_ascii=False)
            else:
                diqu = li.find_all('font')[-1].text.strip()
                diqu = re.findall(r'\[(.*)\]', diqu)[0]
                info = json.dumps({'diqu': diqu}, ensure_ascii=False)
        except:
            info = None

        tmp = [title, span, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, "//table[@id='MoreInfoList1_DataGrid1']/tbody/tr[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//td[@class='huifont']")
        total = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = re.findall(r'/(\d+)', total)[0]
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@id='tblInfo']")
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
    div = soup.find('table', id='tblInfo')
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


data = [
    ["gcjs_zhaobiao_shigong_gg",
     "http://ztb.xjjs.gov.cn/xjweb/jyxx/004001/004001001/MoreInfo.aspx?CategoryNum=004001001",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'施工'}), f2],

    ["gcjs_zhaobiao_fuwu_gg",
     "http://ztb.xjjs.gov.cn/xjweb/jyxx/004001/004001002/MoreInfo.aspx?CategoryNum=004001002",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'服务'}), f2],

    ["gcjs_zhaobiao_huowu_gg",
     "http://ztb.xjjs.gov.cn/xjweb/jyxx/004001/004001003/MoreInfo.aspx?CategoryNum=004001003",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'货物'}), f2],

    ["gcjs_zhaobiao_tielushigong_gg",
     "http://ztb.xjjs.gov.cn/xjweb/jyxx/004001/004001006/004001006001/MoreInfo.aspx?CategoryNum=004001006001",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'施工','jylx':'铁路工程'}), f2],
    #
    ["gcjs_zhaobiao_tielufuwu_gg",
     "http://ztb.xjjs.gov.cn/xjweb/jyxx/004001/004001006/004001006002/MoreInfo.aspx?CategoryNum=004001006002",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'服务','jylx':'铁路工程'}), f2],
    #
    ["gcjs_zhaobiao_tieluhuowu_gg",
     "http://ztb.xjjs.gov.cn/xjweb/jyxx/004001/004001006/004001006003/MoreInfo.aspx?CategoryNum=004001006003",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'货物','jylx':'铁路工程'}), f2],

    ["gcjs_zhongbiaohx_shigong_gg",
     "http://ztb.xjjs.gov.cn/xjweb/jyxx/004002/004002001/MoreInfo.aspx?CategoryNum=004002001",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'施工'}), f2],

    ["gcjs_zhongbiaohx_fuwu_gg",
     "http://ztb.xjjs.gov.cn/xjweb/jyxx/004002/004002002/MoreInfo.aspx?CategoryNum=004002002",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'服务'}), f2],

    ["gcjs_zhongbiaohx_huowu_gg",
     "http://ztb.xjjs.gov.cn/xjweb/jyxx/004002/004002003/MoreInfo.aspx?CategoryNum=004002003",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'货物'}), f2],

    ["gcjs_zhongbiaohx_tielushigong_gg",
     "http://ztb.xjjs.gov.cn/xjweb/jyxx/004002/004002006/004002006001/MoreInfo.aspx?CategoryNum=004002006001",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'施工','jylx':'铁路工程'}), f2],

    ["gcjs_zhongbiaohx_tielufuwu_gg",
     "http://ztb.xjjs.gov.cn/xjweb/jyxx/004002/004002006/004002006002/MoreInfo.aspx?CategoryNum=004002006002",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'服务','jylx':'铁路工程'}), f2],

    ["gcjs_zhongbiaohx_tieluhuowu_gg",
     "http://ztb.xjjs.gov.cn/xjweb/jyxx/004002/004002006/004002006003/MoreInfo.aspx?CategoryNum=004002006003",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'货物','jylx':'铁路工程'}), f2],

    ["gcjs_gqita_zntzs_shigong_gg",
     "http://ztb.xjjs.gov.cn/xjweb/jyxx/004006/004006001/MoreInfo.aspx?CategoryNum=004006001",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': '施工','gglx':'中标通知书'}), f2],

    ["gcjs_gqita_zntzs_fuwu_gg",
     "http://ztb.xjjs.gov.cn/xjweb/jyxx/004006/004006003/MoreInfo.aspx?CategoryNum=004006003",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': '服务', 'gglx': '中标通知书'}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="新疆省省会", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang2", "xinjiang_shenghui"])
    #
    # 修改日期：2019/5/17