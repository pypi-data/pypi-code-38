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

_name_ = "beijingshi"


def f1(driver, num):
    locator = (By.XPATH, '//table[@class="contentTable"]//tr[@name="link"][1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath(
        '//div[@class="page"]//span[@class="active"]').text

    if num != int(cnum):
        val = driver.find_element_by_xpath(
            '//table[@class="contentTable"]//tr[@name="link"][1]').get_attribute('data-url')[-30:-5]

        search_button = driver.find_element_by_xpath(
            '//input[@class="jump-ipt"]')
        driver.execute_script(
            "arguments[0].value = '%s';" %
            num, search_button)

        click_button = driver.find_element_by_xpath('//a[@class="jump-btn"]')
        driver.execute_script("arguments[0].click()", click_button)

        locator = (
            By.XPATH,
            '//table[@class="contentTable"]//tr[@name="link"][1][not(contains(@data-url, "%s"))]' %
            val)
        WebDriverWait(
            driver, 10).until(
            EC.presence_of_element_located(locator))
    data=[]
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    cons = soup.find(
        'table',
        class_='contentTable').find_all(
        'tr',
        attrs={
            'name': 'link'})
    for con in cons:
        tds = con.find_all('td')
        href = con['data-url']
        xm_code = tds[0].get_text().strip()
        name = tds[1].get_text().strip()
        if len(tds) == 6:

            xm_dw = tds[2].get_text().strip()
            xm_type = tds[3].get_text().strip()
            lx_dw = tds[4].get_text().strip()
            ggstart_time = tds[5].get_text().strip()
            info = json.dumps({'xm_dw': xm_dw,
                               'xm_type': xm_type,
                               'lx_dw': lx_dw,
                               'xm_code': xm_code},
                              ensure_ascii=False)
        else:
            shixiang_name = tds[2].get_text().strip()
            ggstart_time = tds[3].get_text().strip()
            jieguo = tds[4].get_text().strip()
            info = json.dumps({'shixiang': shixiang_name,
                               'jieguo': jieguo,
                               'xm_code': xm_code},
                              ensure_ascii=False)

        if 'http' in href:
            href = href
        else:
            href = 'http://tzxm.beijing.gov.cn' + href

        tmp = [name,  ggstart_time, href, info]

        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.XPATH, '//table[@class="contentTable"]//tr[@name="link"][1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath(
        '//div[@id="Pagination"]/a[last()-2]').get_attribute('data-page')
    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="detailOuter"][string-length()>50]')
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
    div = soup.find('div', class_="detailOuter")

    return div


data = [
    ["xm_beian_gg",
     "http://tzxm.beijing.gov.cn/information/project",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["xm_shenpi_gg",
     "http://tzxm.beijing.gov.cn/information/examine",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data,interval_page=1000,num=20, diqu="北京市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(
        conp=[
            "postgres",
            "since2015",
            "192.168.3.171",
            "zlshenpi",
            "beijingshi"],
        )
    # driver = webdriver.Chrome()
    # for d in data:
    #     driver.get(d[1])
    #     print(d[1])
    #     f1(driver,2)
