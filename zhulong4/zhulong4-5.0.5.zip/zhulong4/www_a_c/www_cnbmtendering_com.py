import math
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
import requests
import json

from zhulong4.util.etl import est_tbs, est_meta, est_html, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url = "http://www.fqztb.com/Home/tenderList?index=3&type=%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE"
# driver = webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_ = 'www_cnbmtendering_com'


def f1(driver, num):
    locator = (By.XPATH, '//table[@class="dr-table rich-table "]/tbody/tr[10]//td[6]/a')
    WebDriverWait(driver, 60).until(EC.presence_of_element_located(locator))

    content_page=driver.page_source

    cnum=re.findall('<input type="hidden" id="pageIndex" name="bidNoticePaging.pageIndex" value="(\d+)"',content_page)[0]


    if num != int(cnum):
        val = driver.find_element_by_xpath(
            '//table[@class="dr-table rich-table "]/tbody/tr[10]//td[6]/a').get_attribute('href')[-30:]

        driver.execute_script("""
            (function noTab(page_index,id){
            document.getElementById("pageIndex").value=page_index;
            //$("#"+id).submit();
            document.getElementById(id).submit();
            })(%d,'findNoticsform')""" % num)

        try:
            locator = (
            By.XPATH, '//table[@class="dr-table rich-table "]/tbody/tr[10]//td[6]/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 60).until(EC.presence_of_element_located(locator))
        except:
            if num == page_total:
                locator = (By.XPATH, '//table[@class="dr-table rich-table "]/tbody/tr[1]//td[6]/a')
                WebDriverWait(driver, 60).until(EC.presence_of_element_located(locator))
            else:
                raise TimeoutError

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', class_='dr-table rich-table ').find('tbody')
    trs = div.find_all('tr')

    for tr in trs:
        tds = tr.find_all('td')

        href = tds[2].a['href']
        name = tds[2].a['title']
        ggstart_time = tds[0].get_text().strip()
        index_num = tds[1].get_text().strip()
        cgdw = tds[3].get_text().strip()
        if 'http' in href:
            href = href
        else:
            href = 'http://www.cnbmtendering.com' + href

        info = {'index_num': index_num, 'cgdw': cgdw}
        info = json.dumps(info, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]

        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df

def f4(driver,num):
    locator = (By.XPATH, '//table[@class="dr-table rich-table "]/tbody/tr[10]//td[4]/a')
    WebDriverWait(driver, 60).until(EC.presence_of_element_located(locator))

    content_page = driver.page_source

    cnum =re.findall('<input type="hidden" id="pageIndex" name="bidContPubInfoPaging.pageIndex" value="(\d+)"', content_page)[0]

    if num != int(cnum):
        val = driver.find_element_by_xpath(
            '//table[@class="dr-table rich-table "]/tbody/tr[10]//td[4]/a').get_attribute('href')[-30:]

        driver.execute_script("""
                (function noTab(page_index,id){
                document.getElementById("pageIndex").value=page_index;
                //$("#"+id).submit();
                document.getElementById(id).submit();
                })(%d,'findNoticsform')""" % num)

        try:
            locator = (
                By.XPATH,
                '//table[@class="dr-table rich-table "]/tbody/tr[10]//td[4]/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 60).until(EC.presence_of_element_located(locator))
        except:
            if num == page_total:
                locator = (By.XPATH, '//table[@class="dr-table rich-table "]/tbody/tr[1]//td[4]/a')
                WebDriverWait(driver, 60).until(EC.presence_of_element_located(locator))
            else:
                raise TimeoutError

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', class_='dr-table rich-table ').find('tbody')
    trs = div.find_all('tr')

    for tr in trs:
        tds = tr.find_all('td')

        href = tds[2].a['href']
        name = tds[1].span['title']
        ggstart_time = '1'
        index_num = tds[0].get_text().strip()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.cnbmtendering.com' + href

        info = {'index_num': index_num}
        info = json.dumps(info, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]

        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df

def f5(driver,num):
    locator = (By.XPATH, '//table[@class="dr-table rich-table "]/tbody/tr[10]//a')
    WebDriverWait(driver, 60).until(EC.presence_of_element_located(locator))

    content_page = driver.page_source

    cnum =re.findall('var currpage = parseInt\("(\d+)"\)', content_page)[0]


    if num != int(cnum):
        val = driver.find_element_by_xpath(
            '//table[@class="dr-table rich-table "]/tbody/tr[10]//a').get_attribute('href')[-30:]

        driver.execute_script("""
                (function change_page(page){
			    currpage = page;
			    $("#f_currpage").val(currpage);
			    $("#selectForm").submit();
		        })(%d)""" %num)

        try:
            locator = (
                By.XPATH,
                '//table[@class="dr-table rich-table "]/tbody/tr[10]//a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 60).until(EC.presence_of_element_located(locator))
        except:
            if num == page_total:
                locator = (By.XPATH, '//table[@class="dr-table rich-table "]/tbody/tr[1]//a')
                WebDriverWait(driver, 60).until(EC.presence_of_element_located(locator))
            else:
                raise TimeoutError

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', class_='dr-table rich-table ').find('tbody')
    trs = div.find_all('tr')

    for tr in trs:
        tds = tr.find_all('td')

        href = tds[4].a['href']
        cgdw=tds[0].get_text()
        name = tds[2].get_text()
        ggstart_time = tds[3].get_text()
        ggstart_time=re.findall('\d+-\d+-\d+',ggstart_time)[0]
        index_num = tds[1].get_text().strip()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.cnbmtendering.com/bidms/' + href

        info = {'index_num': index_num,'cgdw':cgdw}
        info = json.dumps(info, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]

        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df


def f6(driver,num):
    locator = (By.XPATH, '//table[@class="dr-table rich-table "]/tbody/tr[1]/td[2]')
    WebDriverWait(driver, 60).until(EC.presence_of_element_located(locator))

    content_page = driver.page_source

    cnum =re.findall('var currpage = parseInt\("(\d+)"\)', content_page)[0]


    if num != int(cnum):
        val = driver.find_element_by_xpath(
            '//table[@class="dr-table rich-table "]/tbody/tr[1]/td[2]').text

        driver.execute_script("""
                (function change_page(page){
			    currpage = page;
			    $("#f_currpage").val(currpage);
			    $("#selectForm").submit();
		        })(%d)""" %num)


        locator = (
            By.XPATH,
            '//table[@class="dr-table rich-table "]/tbody/tr[1]/td[2][not(contains(string(),"%s"))]' % val)
        WebDriverWait(driver, 60).until(EC.presence_of_element_located(locator))


    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', class_='dr-table rich-table ').find('tbody')
    trs = div.find_all('tr')

    for tr in trs:
        tds = tr.find_all('td')
        href =tds[1].get_text().strip()
        cgdw=tds[0].get_text()
        name = tds[2].get_text()
        wl_name=tds[4].get_text()
        xinghao=tds[5].get_text()
        zb_company=tds[6].get_text()
        zb_number=tds[7].get_text()
        ggstart_time = tds[3].get_text()

        index_num = tds[1].get_text().strip()

        info = {'index_num': index_num,'cgdw':cgdw,
                'wl_name':wl_name,'xinghao':xinghao,
                'zhongbiao_company':zb_company,'zhongbiao_count':zb_number,
                'hreftype':'不可抓网页'}
        info = json.dumps(info, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]

        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df


def f7(driver):
    locator = (By.XPATH, '//td[@class="dr-table-footercell rich-table-footercell"]/a[1]')
    WebDriverWait(driver, 40).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//td[@class="dr-table-footercell rich-table-footercell"]').text
    total = re.findall('共有(\d+)条记录', total)[0]
    total = math.ceil(int(total) / 10)

    total = int(total)

    driver.quit()
    return total


def f2(driver):
    global page_total
    locator = (By.XPATH, '//table[@class="dr-table rich-table "]/tbody/tr[10]//td[last()]/a')
    WebDriverWait(driver, 40).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//table[@class="dr-table rich-table "]/tfoot//td').text
    total = re.findall('共有(\d+)条记录', total)[0]
    total = math.ceil(int(total) / 10)

    total = int(total)
    page_total=total
    driver.quit()

    return total



def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//div[@class="body_content"][string-length()>10] | //div[@id="main"][string-length()>10]')

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    time.sleep(0.1)
    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 10: break

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    div = soup.find('div', class_="body_content")

    if div == None:
        div=soup.find('div',id="main")

    return div


data = [

    ["qy_zhaobiao_gg", "http://www.cnbmtendering.com/bidms/noticeBase!selBidNoticeList.action",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_zhongbiao_gg", "http://www.cnbmtendering.com/bidms/contPubInfoAction!selBidContent.action",["name", "ggstart_time", "href", "info"], f4, f2],
    ["qy_zhaobiao_caigou_gg", "http://www.cnbmtendering.com/bidms/purchaseInfo_toQianList",["name", "ggstart_time", "href", "info"], add_info(f5,{'tag':'集中采购'}), f2],
    ["qy_zhaobiao_yuancailiao_gg", "http://www.cnbmtendering.com/bidms/bulkInfo_toQianList",["name", "ggstart_time", "href", "info"], add_info(f5,{"tag":"原材料集中采购"}), f2],
    ["qy_gqita_xiaoshou_gg", "http://www.cnbmtendering.com/bidms/saleInfo_toQianList",["name", "ggstart_time", "href", "info"], add_info(f5,{'tag':'集中销售'}), f2],

    ["qy_zhongbiao_caigou_gg", "http://www.cnbmtendering.com/bidms/purchaseBid_toQianList",["name", "ggstart_time", "href", "info"], add_info(f6,{'tag':'集中采购'}), f7],
    ["qy_zhongbiao_yuancailiao_gg", "http://www.cnbmtendering.com/bidms/bulkBid_toQianList",["name", "ggstart_time", "href", "info"], add_info(f6,{'tag':'原材料采购'}), f7],
    ["qy_gqita_chengjiao_gg", "http://www.cnbmtendering.com/bidms/saleBid_toQianList",["name", "ggstart_time", "href", "info"], add_info(f6,{'tag':'集中销售成交'}), f7],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="中国建材集团", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch3", "www_cnbmtendering_com"],pageLoadStrategy='none',pageloadtimeout=80)
    pass