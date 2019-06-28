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

import json

import time

from zhulong.util.etl import est_html, est_meta, add_info

_name_ = "zhaoqing"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='column-info-list']/ul/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    flag = None
    if 'moreinfolist.aspx' not in url:
        flag = 1
    if flag:
        locator = (By.XPATH, "//a[contains(@class,'current')]")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    else:
        cnum = int(re.findall("(?<=Paging=)[0-9]{1,}", url)[0])
    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='column-info-list']/ul/li[last()]/a").get_attribute('href')[-40:]
        if flag:
            driver.execute_script("ShowAjaxNewPage(window.location.pathname,'categorypagingcontent',%d)"%num)
        else:
            url = re.sub("(?<=Paging=)[0-9]{1,}", str(num), url)
            driver.get(url)
        locator = (By.XPATH, "//div[@class='column-info-list']/ul/li[last()]/a[not(contains(@href, '%s'))]"% val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("div", class_="column-info-list")
    ul = div.find("ul")
    lis = ul.find_all("li", class_="clearfix")
    data = []
    for li in lis:
        a = li.find("a")
        try:
            name = a['title'].strip()
        except:
            name = a.text.strip()
        span = li.find("span")
        tmp = [name, "http://ggzy.zhaoqing.gov.cn" + a["href"], span.text.strip()]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='column-info-list']")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='pagemargin']//td[@class='huifont'] | //a[@class='wb-page-default wb-page-number wb-page-family']")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath("//div[@class='pagemargin']//td[@class='huifont'] | //a[@class='wb-page-default wb-page-number wb-page-family']").text.split("/")[1]
    total = int(total)
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.CLASS_NAME, "menu-info")

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    before = len(driver.page_source)
    time.sleep(0.5)
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

    div = soup.find('div', class_="menu-info")
    # div=div.find_all('div',class_='ewb-article')[0]

    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://ggzy.zhaoqing.gov.cn/zqfront/showinfo/moreinfolist.aspx?categorynum=003001001&Paging=1",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://ggzy.zhaoqing.gov.cn/zqfront/showinfo/moreinfolist.aspx?categorynum=003001002&Paging=1",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://ggzy.zhaoqing.gov.cn/zqfront/showinfo/moreinfolist.aspx?categorynum=003001003&Paging=1",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://ggzy.zhaoqing.gov.cn/zqfront/showinfo/moreinfolist.aspx?categorynum=003002001&Paging=1",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://ggzy.zhaoqing.gov.cn/zqfront/showinfo/moreinfolist.aspx?categorynum=003002002&Paging=1",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://ggzy.zhaoqing.gov.cn/zqfront/showinfo/moreinfolist.aspx?categorynum=003002003&Paging=1",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_zhaobiao_yiban_gg", "http://ggzy.zhaoqing.gov.cn/zqfront/jyxx/003006/003006001/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '一般招标'}), f2],

    ["zfcg_biangeng_yiban_gg", "http://ggzy.zhaoqing.gov.cn/zqfront/jyxx/003006/003006002/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '一般招标'}), f2],

    ["zfcg_zhongbiaohx_yiban_gg", "http://ggzy.zhaoqing.gov.cn/zqfront/jyxx/003006/003006003/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '一般招标'}), f2],

    ["zfcg_zhongbiao_yiban_gg", "http://ggzy.zhaoqing.gov.cn/zqfront/jyxx/003006/003006004/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '一般招标'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省肇庆市", **args)
    est_html(conp, f=f3, **args)

# 修改日期2019/6/24
# 增加公告
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "127.0.0.1", "guangdong", "zhaoqing"])



