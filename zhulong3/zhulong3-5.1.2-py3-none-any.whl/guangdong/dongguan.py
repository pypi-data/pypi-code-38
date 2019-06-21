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

from zhulong3.util.etl import est_tbs, est_meta, est_html, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url = "http://www.fzztb.com/CmsPortalWeb/main/project.xhtml"
# driver = webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_ = 'guangdong_dongguan'


def f1(driver, num):
    locator = (By.XPATH, '//table[@id="ctl00_cph_context_GridView1"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum=int(driver.find_element_by_xpath('//table[@class="gridview_pagerTemplateStyle"]//font[@color="red"][1]').text)
    print(cnum)

    if cnum != num:
        val = driver.find_element_by_xpath('//table[@id="ctl00_cph_context_GridView1"]//tr[2]//a').get_attribute('href')[-30:]
        inp=driver.find_element_by_xpath('//table[@class="gridview_pagerTemplateStyle"]//input[@type="text"]')

        driver.execute_script("arguments[0].value = '%s';"%num, inp)
        sub=driver.find_element_by_xpath('//table[@class="gridview_pagerTemplateStyle"]//input[@type="submit"]')
        driver.execute_script("arguments[0].click();", sub)

        locator = (By.XPATH, '//table[@id="ctl00_cph_context_GridView1"]//tr[2]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))


    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find('table', id='ctl00_cph_context_GridView1').find_all('tr')[1:]

    for tr in trs:
        tds = tr.find_all('td')
        href = tr.find('a')['href']
        name = tr.find('a').get_text().strip()
        procode=tds[1].get_text().strip()
        dw=tds[3].get_text().strip()
        ggstart_time = tds[-1].get_text().strip()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.dgzb.com.cn:8080/dgjyweb/sitemanage/' + href
        info={'procode':procode,'dw':dw}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time,href, info]
        print(tmp)
        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//table[@id="ctl00_cph_context_GridView1"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//table[@class="gridview_pagerTemplateStyle"]//font[@color="red"][2]').text

    total = int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//table[@class="weizi"]/following-sibling::table[1][string-length()>50]')

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
        if i > 5: break

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    div = soup.find('table', class_="zhiwei").parent

    return div


data = [


    ["gcjs_zhaobiao_diqu1_gg", "http://www.dgzb.com.cn:8080/dgjyweb/sitemanage/GxInfo_List.aspx?ModeId=1&clearPaging=true",["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu':'市级'}), f2],
    ["gcjs_gqita_da_bian_diqu1_gg", "http://www.dgzb.com.cn:8080/dgjyweb/sitemanage/GcBuchongList.aspx?ModeId=2&clearPaging=true",["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu':'市级'}), f2],
    ["gcjs_zhongbiao_diqu1_gg", "http://www.dgzb.com.cn:8080/dgjyweb/sitemanage/GxInfo_List.aspx?ModeId=4&clearPaging=true",["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu':'市级'}), f2],

    ["gcjs_zhaobiao_diqu2_gg", "http://www.dgzb.com.cn:8080/dgjyweb/sitemanage/Town_zbList.aspx?clearPaging=true",["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu':'镇区'}), f2],
    ["gcjs_gqita_da_bian_diqu2_gg", "http://www.dgzb.com.cn:8080/dgjyweb/sitemanage/Town_zbBcList.aspx?clearPaging=true",["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu':'镇区'}), f2],
    ["gcjs_zhongbiao_diqu2_gg", "http://www.dgzb.com.cn:8080/dgjyweb/sitemanage/Town_gsList.aspx?clearPaging=true",["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu':'镇区'}), f2],

]

def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省东莞市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "guangdong_dongguan"],headless=False,num=1,total=4)