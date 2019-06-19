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

_name_ = "anhuisheng"


def f1(driver, num):
    locator = (By.XPATH, '//table[@id="proTable"]/tbody/tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath(
        '//div[@class="qmanu"]').text
    cnum=re.findall('上一页(.+?)下一页',cnum)[0].strip()

    if num != int(cnum):
        val = driver.find_element_by_xpath(
            '//table[@id="proTable"]/tbody/tr[2]//a').get_attribute('onclick')[-30:-2]

        driver.execute_script('$("#pageNo").val(%d);$("#publicInformationForm").submit();'%num)

        locator = (
            By.XPATH,
            '//table[@id="proTable"]/tbody/tr[2]//a[not(contains(@onclick, "%s"))]' %
            val)
        WebDriverWait(
            driver, 10).until(
            EC.presence_of_element_located(locator))
    data=[]
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    cons = soup.find('table',id='proTable').find_all('tr')[1:]
    for con in cons:
        tds = con.find_all('td')
        href = tds[0].a['onclick']
        name = tds[0]['title']
        xm_code=re.findall('[-\d]+',name)[0]
        shixiang = tds[1]['title'].strip()
        bumen = tds[2].get_text().strip()
        jieguo = tds[3].get_text().strip()
        ggstart_time = tds[4].get_text()
        if not ggstart_time:
            ggstart_time='not'

        info = json.dumps({'shixiang': shixiang, 'bumen': bumen, 'jieguo': jieguo, 'xm_code': xm_code},
                          ensure_ascii=False)

        href='http://tzxm.ahzwfw.gov.cn'+re.findall("window.open\('(.+)'\)",href)[0]

        tmp = [name,  ggstart_time, href, info]


        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.XPATH, '//table[@id="proTable"]/tbody/tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath(
        '//div[@class="qmanu"]').text
    total=re.findall('共(.+?)页',total)[0].strip()
    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@id="regmain"][string-length()>50]')
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
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', id="regmain")

    return div


data = [

    ["xm_shenpi_gg",
     "http://tzxm.ahzwfw.gov.cn/portalopenPublicInformation.do?method=queryExamineAll",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data,interval_page=1000,num=20, diqu="安徽省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(
        conp=[
            "postgres",
            "since2015",
            "192.168.3.171",
            "zlshenpi",
            "anhuisheng"],
        )
    # driver = webdriver.Chrome()
    # for d in data:
    #     driver.get(d[1])
    #     print(d[1])
    #     f1(driver,2)
