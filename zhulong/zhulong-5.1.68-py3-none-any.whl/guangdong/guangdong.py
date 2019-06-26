import json

import pandas as pd
import re
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
from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, add_info, est_gg,est_meta_large



_name_ = 'guangdong'

def f1(driver, num):
    locator = (By.XPATH, '//table[@class="table"]/tbody/tr[1]//a')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    cnum=int(driver.find_element_by_xpath('//div[@id="page_new"]//font[@color="blue"]').text)


    if cnum != num:
        val = driver.find_element_by_xpath(
            '//table[@class="table"]/tbody/tr[1]//a').get_attribute('href')
        val=re.findall('bulletinId=(.+?)&',val)[0]

        driver.execute_script('goPage(%d)'%num)

        locator = (
            By.XPATH, "//table[@class='table']/tbody/tr[1]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("table", class_="table").find('tbody')
    dls = div.find_all("tr",recursive=False)

    data = []
    for dl in dls:

        name = dl.find('a').parent['title']
        href = dl.find('a')['href']
        ggstart_time = dl.find_all('td')[-1].get_text().strip()
        diqu = dl.find_all('td')[-2].get_text()

        info=json.dumps({"diqu":diqu},ensure_ascii=False)

        if 'http' in href:
            href = href
        else:
            href = 'http://bs.gdggzy.org.cn' + href

        tmp = [name, ggstart_time, href, info]

        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df



def f4(driver, num):
    locator = (By.XPATH, '//div[@class="pub_cont06"]/div[1]/li[1]//a')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    cnum=int(driver.find_element_by_xpath('//input[@class="manage_paging_input"]').get_attribute('value'))

    if cnum != num:
        val = driver.find_element_by_xpath(
            '//div[@class="pub_cont06"]/div[1]/li[1]//a').get_attribute('onclick')
        val=re.findall("detailNewsWb\('(.+?)'\)",val)[0]
        driver.execute_script('gotoPage(%d)'%num)

        locator = (
            By.XPATH, "//div[@class='pub_cont06']/div[1]/li[1]//a[not(contains(@onclick,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("div", class_="pub_cont06").find('div')
    dls = div.find_all("li",recursive=False)

    data = []
    for dl in dls:

        name = dl.find('a').get_text().strip()
        href = dl.find('a')['onclick']
        ggstart_time = dl.find('span',class_='span_time').get_text().strip()


        if 'http' in href:
            href = href
        else:
            href = re.findall("detailNewsWb\('(.+?)'\)",href)[0]
            href = 'http://www.gpcgd.com/gpcgd/portal/portal-news!detailNewsWb?portalNews.id=' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df

def f5(driver):
    locator = (By.XPATH, '//div[@class="pub_cont06"]/div[1]/li[1]//a')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//div[@class="manage_paging_box"]/span[@class="orange"][1]').text.strip()

    driver.quit()

    return int(total)



def f2(driver):
    locator = (By.XPATH, '//table[@class="table"]/tbody/tr[1]//a')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    total=driver.find_element_by_xpath('//div[@id="page_new"]/a[last()]').get_attribute('href')
    total=re.findall('goPage\((\d+)\)',total)[0]

    driver.quit()

    return int(total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="cell"][string-length()>50] | //div[@class="detial"][string-length()>50]')
    WebDriverWait(
        driver, 10).until(
        EC.presence_of_all_elements_located(locator))

    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 5:
            break

    # f3 情况1
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_='cell')
    if div == None:
        div=soup.find('div',class_='pub_cont_details')

    return div


data = [

    ["gcjs_zhaobiao_gg",
     "http://bs.gdggzy.org.cn/osh-web/project/projectbulletin/bulletinList?queryType=1&tradeTypeId=Construction&tradeItemId=gc_res_bulletin",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["gcjs_zhongbiaohx_gg",
     "http://bs.gdggzy.org.cn/osh-web/project/projectbulletin/bulletinList?queryType=3&tradeTypeId=Construction&tradeItemId=gc_res_result",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["zfcg_zhaobiao_gg",
     "http://bs.gdggzy.org.cn/osh-web/project/projectbulletin/bulletinList?queryType=1&tradeTypeId=GovernmentProcurement&tradeItemId=zf_res_bulletin",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://bs.gdggzy.org.cn/osh-web/project/projectbulletin/bulletinList?queryType=3&tradeTypeId=GovernmentProcurement&tradeItemId=zf_res_result",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_piliang_gg",
     "http://www.gpcgd.com/gpcgd/portal/portal-news!listNews?portalNews.typeId=90011",
     ["name", "ggstart_time", "href", "info"], add_info(f4,{"zbfs":"批量集中采购"}), f5],
    ["zfcg_zhaobiaohx_piliang_gg",
     "http://www.gpcgd.com/gpcgd/portal/portal-news!listNews?portalNews.typeId=90013",
     ["name", "ggstart_time", "href", "info"], add_info(f4,{"zbfs":"批量集中采购"}), f5],
    ["zfcg_biangeng_piliang_gg",
     "http://www.gpcgd.com/gpcgd/portal/portal-news!listNews?portalNews.typeId=90014",
     ["name", "ggstart_time", "href", "info"], add_info(f4,{"zbfs":"批量集中采购"}), f5],

    ["zfcg_zhaobiao_jizhong_gg",
     "http://www.gpcgd.com/gpcgd/portal/portal-news!listNews?portalNews.typeId=40011",
     ["name", "ggstart_time", "href", "info"], add_info(f4,{"zbfs":"集中采购"}), f5],

    ["zfcg_zhongbiao_jizhong_gg",
     "http://www.gpcgd.com/gpcgd/portal/portal-news!listNews?portalNews.typeId=40012",
     ["name", "ggstart_time", "href", "info"], add_info(f4,{"zbfs":"集中采购"}), f5],

    ["zfcg_yucai_jizhong_gg",
     "http://www.gpcgd.com/gpcgd/portal/portal-news!listNews?portalNews.typeId=40013",
     ["name", "ggstart_time", "href", "info"], add_info(f4,{"zbfs":"集中采购"}), f5],

    ["zfcg_gqita_da_bian_jizhong_gg",
     "http://www.gpcgd.com/gpcgd/portal/portal-news!listNews?portalNews.typeId=40014",
     ["name", "ggstart_time", "href", "info"], add_info(f4,{"zbfs":"集中采购"}), f5],

    ["zfcg_zgys_jizhong_gg",
     "http://www.gpcgd.com/gpcgd/portal/portal-news!listNews?portalNews.typeId=40015",
     ["name", "ggstart_time", "href", "info"], add_info(f4,{"zbfs":"集中采购"}), f5],

    ["zfcg_zhongbiaohx_jizhong_gg",
     "http://www.gpcgd.com/gpcgd/portal/portal-news!listNews?portalNews.typeId=40016",
     ["name", "ggstart_time", "href", "info"], add_info(f4,{"zbfs":"集中采购"}), f5],


]


def work(conp, **args):
    est_meta_large(conp, data=data,interval_page=1000,num=20, diqu="广东省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(
        conp=[
            "postgres",
            "since2015",
            '192.168.3.171',
            "guangdong",
            "guangdong"],
        headless=False,
        num=1,
        total=2)
