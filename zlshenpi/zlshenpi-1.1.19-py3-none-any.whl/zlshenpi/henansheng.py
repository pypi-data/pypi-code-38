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
from zlshenpi.util.etl import add_info, est_meta, est_html, est_tbs, add_info,est_meta_large
import sys
import time
import json

_name_ = "henansheng"


def f1(driver, num):
    locator = (By.XPATH, '//table[@class="table nurmalTable t3_nurmalTable1"]/tbody/tr[not(@style)][1]/td[last()]/input')
    val = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).get_attribute("onclick")[-30:]
    # print(val)
    locator = (By.XPATH, "//td[@align='center']")
    cnum_temp = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text
    cnum = int(re.findall('(\d+)\/',cnum_temp)[0])
    if num != int(cnum):
        driver.execute_script("_gotoPage('%s');" % num)
        locator = (By.XPATH, """//table[@class="table nurmalTable t3_nurmalTable1"]/tbody/tr[not(@style)][1]/td[last()]/input[not(contains(@onclick, "%s"))]""" % val)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    body = etree.HTML(page)
    contents = body.xpath('//table[@class="table nurmalTable t3_nurmalTable1"]/tbody/tr[not(@style)]')

    data = []
    for content in contents:
        xm_code = content.xpath('./td/span/text()')[0].strip()
        name = content.xpath("./td[2]/text()")[0].strip()

        txt_tmp = content.xpath('./td[last()]/input/@onclick')[0].strip()
        projectcode = re.findall("\'([^']+?)\'", txt_tmp)[0]
        href = "http://tzls.hazw.gov.cn/getsxinfo.jspx?proid=" + projectcode

        shixiang = content.xpath('./td[3]/text()')[0].strip()
        status = content.xpath('./td[4]/text()')[0].strip()

        ggstart_time = content.xpath('./td[5]/text()')[0].strip()
        info = json.dumps({"shixiang": shixiang, 'status': status, "xm_code": xm_code}, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)

    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.XPATH, "//td[@align='center']")
    total_page_temp = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text
    total_page = int(re.findall('\/(\d+)',total_page_temp)[0])
    driver.quit()
    return total_page


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='div_one']")
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('div', class_="div_one")
    return div


data = [
    ["xm_jieguo_gg",
     "http://tzls.hazw.gov.cn/jggs.jspx?apply_date_begin=2017-01-31&pageNo=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="河南省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlshenpi", "henansheng"])
    # driver = webdriver.Chrome()
    # for d in data:
    #     driver.get(d[1])
        # print(d[1])
        # for i in range(1356,1360):
        #     print(f1(driver, i))
    # print(f2(driver))