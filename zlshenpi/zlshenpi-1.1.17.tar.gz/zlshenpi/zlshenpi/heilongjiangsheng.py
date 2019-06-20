import math

import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zlshenpi.util.etl import add_info, est_meta, est_html, est_tbs, add_info, est_meta_large
import sys
import time
import json

_name_ = "heilongjiangsheng"


def f1(driver, num):
    locator = (By.XPATH, '(//table[@class="gridtable"]//tr[2]//a)[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//ul[@id="page"]/li[2]//span').text
    cnum=re.findall('(\d+?)/',cnum)[0]

    if num != int(cnum):
        val = driver.find_element_by_xpath('(//table[@class="gridtable"]//tr[2]//a)[1]').get_attribute(
            'onclick')[-50:-2]

        driver.execute_script("""
    document.getElementById('page').value=%d;
    document.getElementById("npage").name="action";
    document.getElementById("npage").value="index";
    document.getElementById("leafNumber").value = document.getElementById("page").value;
    doSel();"""%num)

        locator = (
        By.XPATH, '(//table[@class="gridtable"]//tr[2]//a)[1][not(contains(@onclick, "%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data=[]
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    cons = soup.find('table', class_='gridtable').find('tbody').find_all('tr')[1:]
    for con in cons:
        tds = con.find_all('td')
        href = tds[0].a['onclick']
        name = tds[1].find('a').get_text().strip()
        xm_code = tds[0].get_text().strip()

        shixiang = tds[2].get_text().strip()
        bumen = tds[3].get_text().strip()
        jieguo = tds[4].get_text().strip()
        ggstart_time = tds[5].get_text()
        info = json.dumps({'shixiang': shixiang, 'bumen': bumen,  'jieguo': jieguo,'xm_code':xm_code},
                          ensure_ascii=False)

        uuid = re.findall("\('(.+?)'", href)[0]
        pro_code = re.findall(",'(.+?)'\)", href)[0]
        href='http://tzxm.hljzwzx.gov.cn/hz_tzxm_root_hlj/beian/lookInfo?rapi_uuid=%s&project_code=%s'%(uuid,pro_code)

        tmp = [name,  ggstart_time, href, info]
        # print(tmp)
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):



    locator = (By.XPATH, '(//table[@class="gridtable"]//tr[2]//a)[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath('//ul[@id="page"]/li[2]//span').text.strip()
    total=re.findall('/(\d+)',total)[0]
    driver.quit()
    return int(total)


def show_detail(f):
    def inner(*args):
        driver=args[0]
        url=driver.current_url
        if 'detail' not in url:
            locator = (By.XPATH, '//ul[@class="ls4-dybgdul"]/li/a')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            driver.execute_script('gomore()')
            time.sleep(0.5)
            driver.close()
            time.sleep(0.1)
            hands=driver.window_handles
            driver.switch_to.window(hands[0])
            locator = (By.XPATH, '(//table[@class="gridtable"]//tr[2]//a)[1]')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*args)
    return inner


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//body[string-length()>100]')
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
    div = soup.find('body')
    if '已经过了有效期失效不能访问' in page:
        raise ValueError('ip失效')
    return div


data = [


    ["xm_shenpi_gg",
     "http://tzxm.hljzwzx.gov.cn/hz_tzxm_root_hlj/tzxmindex",
     ["name", "ggstart_time", "href", "info"], show_detail(f1), show_detail(f2)],

]


def work(conp, **args):
    est_meta_large(conp, data=data,interval_page=1000,num=20, diqu="黑龙江省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlshenpi", "heilongjiangsheng"], )
    # driver = webdriver.Chrome()
    # for d in data:
    #     driver.get(d[1])
    #     print(d[1])
    #     f1(driver,2)
