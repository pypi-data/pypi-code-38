
import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_command,db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

import json



cod = None
type = None

from zhulong.util.etl import add_info,est_meta,est_html,est_tbs


_name_="fuqing"


def f1(driver, num):
    url = driver.current_url
    if 'cod' in url:
        url = url.rsplit('&', maxsplit=2)[0]
        driver.get(url)
    locator = (By.XPATH, "//pre")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    cnum = re.findall(r'page=(\d+)', url)[0]
    if num != int(cnum):
        html_data = driver.find_element_by_xpath('//pre').text.strip()
        html_data = json.loads(html_data)
        page = html_data['json']['{}'.format(cod)]['tp']
        val1 = page[0]['id']
        if num == 1:
            url = re.sub("page=[0-9]*", "page=1", url)
        else:
            s = "page=%d" % (num) if num > 1 else "page=1"
            url = re.sub("page=[0-9]*", s, url)
            # print(cnum)
        driver.get(url)
        if '500 - 内部服务器错误' in driver.page_source:
            raise TimeoutError
        locator = (By.XPATH, "//pre")
        html_data = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        html_data = json.loads(html_data)
        page = html_data['json']['{}'.format(cod)]['tp']
        val2 = page[0]['id']
        if val1 == val2:
            raise TimeoutError
    html_data = driver.find_element_by_xpath('//pre').text.strip()
    html_data = json.loads(html_data)
    page = html_data['json']['{}'.format(cod)]['tp']
    data = []
    for li in page:
        title = li['Title']
        span = li['publishTime']
        if cod == 'tp':
            link = 'http://www.fqztb.com/fjebid/jypt.html?type=' + type + '&tpid=' + li['id']
        else:
            link = 'http://www.fqztb.com/fjebid/jypt.html?type=' + type + '&tpid=' + li['TpId']
        dd = li['Category']
        info = json.dumps({'leixing': dd}, ensure_ascii=False)
        tmp = [title, span, link, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    global cod,type
    cod = None
    type = None
    url = driver.current_url
    cod = re.findall(r'cod=(.*)&', url)[0]
    type = re.findall(r'type=(.*)', url)[0]
    start_url = url.rsplit('&', maxsplit=2)[0]
    driver.get(start_url)
    locator = (By.XPATH, "//pre")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    html_data = driver.find_element_by_xpath('//pre').text.strip()
    html_data = json.loads(html_data)
    total = html_data['json']['{}'.format(cod)]['total']
    if int(total) / 10 == int(int(total) / 10):
        num = int(int(total) / 10)
    else:
        num = int(int(total) / 10) + 1
    driver.quit()
    return int(num)




def f3(driver, url):
    driver.get(url)
    locator = (By.CLASS_NAME, "main")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    driver.switch_to_frame('myFrame')
    locator = (By.XPATH, "//div[@class='widget'][string-length()>30] | //div[@class='content'][string-length()>30]")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    before = len(driver.page_source)
    time.sleep(1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(1)
        after = len(driver.page_source)
        i += 1
        if i > 5: break
    time.sleep(1)
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_="wrap")
    if div == None:
        div = soup.find('div', id="templateContent")
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.fqztb.com/TenderProject/ListAll?page=1&records=10&category=%E6%88%BF%E5%B1%8B%E5%B8%82%E6%94%BF%2C%E6%B0%B4%E5%88%A9%E5%B7%A5%E7%A8%8B%2C%E5%9B%BD%E5%9C%9F%E8%B5%84%E6%BA%90%2C%E4%BA%A4%E9%80%9A%E8%BF%90%E8%BE%93%2C%E5%86%9C%E4%B8%9A%E7%BB%BC%E5%90%88%E5%BC%80%E5%8F%91%2C%E5%85%B6%E4%BB%96%E8%A1%8C%E4%B8%9A&title=&cod=tp&type=招标公告",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_zhong_liu_gg",
     "http://www.fqztb.com/TenderProject/ListAll?page=1&records=10&category=%E6%88%BF%E5%B1%8B%E5%B8%82%E6%94%BF%2C%E6%B0%B4%E5%88%A9%E5%B7%A5%E7%A8%8B%2C%E5%9B%BD%E5%9C%9F%E8%B5%84%E6%BA%90%2C%E4%BA%A4%E9%80%9A%E8%BF%90%E8%BE%93%2C%E5%86%9C%E4%B8%9A%E7%BB%BC%E5%90%88%E5%BC%80%E5%8F%91%2C%E5%85%B6%E4%BB%96%E8%A1%8C%E4%B8%9A&title=&cod=bid&type=中标公示",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://www.fqztb.com/TenderProject/ListAll?page=1&records=10&category=%E6%88%BF%E5%B1%8B%E5%B8%82%E6%94%BF%2C%E6%B0%B4%E5%88%A9%E5%B7%A5%E7%A8%8B%2C%E5%9B%BD%E5%9C%9F%E8%B5%84%E6%BA%90%2C%E4%BA%A4%E9%80%9A%E8%BF%90%E8%BE%93%2C%E5%86%9C%E4%B8%9A%E7%BB%BC%E5%90%88%E5%BC%80%E5%8F%91%2C%E5%85%B6%E4%BB%96%E8%A1%8C%E4%B8%9A&title=&cod=sup&type=补充通知",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="福建省福清市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.4.175","fujian","fuqing"])

    # driver=webdriver.Chrome()
    # url = "http://www.fqztb.com/TenderProject/ListAll?page=1&records=10&category=%E6%88%BF%E5%B1%8B%E5%B8%82%E6%94%BF%2C%E6%B0%B4%E5%88%A9%E5%B7%A5%E7%A8%8B%2C%E5%9B%BD%E5%9C%9F%E8%B5%84%E6%BA%90%2C%E4%BA%A4%E9%80%9A%E8%BF%90%E8%BE%93%2C%E5%86%9C%E4%B8%9A%E7%BB%BC%E5%90%88%E5%BC%80%E5%8F%91%2C%E5%85%B6%E4%BB%96%E8%A1%8C%E4%B8%9A&title=&cod=bid&type=中标公示"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    # driver = webdriver.Chrome()
    # url = "http://www.fqztb.com/TenderProject/ListAll?page=1&records=10&category=%E6%88%BF%E5%B1%8B%E5%B8%82%E6%94%BF%2C%E6%B0%B4%E5%88%A9%E5%B7%A5%E7%A8%8B%2C%E5%9B%BD%E5%9C%9F%E8%B5%84%E6%BA%90%2C%E4%BA%A4%E9%80%9A%E8%BF%90%E8%BE%93%2C%E5%86%9C%E4%B8%9A%E7%BB%BC%E5%90%88%E5%BC%80%E5%8F%91%2C%E5%85%B6%E4%BB%96%E8%A1%8C%E4%B8%9A&title=&cod=bid&type=中标公示"
    # driver.get(url)
    # for i in range(5, 7):
    #     df=f1(driver, i)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver,f)
    #         print(d)