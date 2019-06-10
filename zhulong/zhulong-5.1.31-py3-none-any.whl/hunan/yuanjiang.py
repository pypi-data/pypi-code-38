import pandas as pd
import re

from lxml import etree
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

from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, add_info

_name_ = "yuanjiang"


def f1(driver, num):
    locator = (By.XPATH, "//td[@valign='top']/table/tbody/tr[@class='sxl02']")
    WebDriverWait(driver, 40).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    if "index" not in url:
        cnum = int(re.findall("([0-9]{1,}).html", url)[0])
    else:
        cnum = 1

    locator = (By.XPATH, "//td[@valign='top']/table/tbody/tr[@class='sxl02']")
    WebDriverWait(driver, 40).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath("//td[@valign='top']/table/tbody/tr[@class='sxl02'][1]/td/a").get_attribute("href")[-40:]
    if cnum != num:
        if "page" in url:
            url = re.sub("([0-9]{1,})\.", str(num) + ".", url)
        else:
            url = re.sub("index.html", "pages" + "/" + str(num) + ".html", url)
        driver.get(url)
        locator = (By.XPATH, "//td[@valign='top']/table/tbody/tr[@class='sxl02'][1]/td/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 40).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    body = etree.HTML(page)
    data = []
    content_list = body.xpath("//td[@valign='top']/table/tbody/tr[@class='sxl02']")

    for content in content_list:
        name = content.xpath("./td/a/text()")[0].strip().strip("・").strip()
        ggstart_time = content.xpath("./td[2]/text()")[0].strip().strip("[").strip("]")
        url = content.xpath("./td/a/@href")[0].strip()
        tmp = [name, ggstart_time, url]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None

    return df


def f2(driver):
    locator = (By.ID, "pages")
    WebDriverWait(driver, 40).until(EC.presence_of_element_located(locator))

    if len(driver.find_elements_by_xpath('//*[@id="pages"]/a')) > 2:
        locator = (By.XPATH, '//*[@id="pages"]/a')
        WebDriverWait(driver, 40).until(EC.presence_of_element_located(locator))

        total = int(
            driver.find_element_by_xpath('//*[@id="pages"]/a[last()-1]').text.strip())
        driver.quit()
        return total
    else:
        driver.quit()
        return 1


def f3(driver, url):
    driver.get(url)

    locator = (By.CLASS_NAME, "xl_x")

    WebDriverWait(driver, 40).until(EC.presence_of_all_elements_located(locator))

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
    div = soup.find('table', class_='xl_x')
    return div


data = [
    ["gcjs_zhaobiao_gg", "http://www.yuanjiang.gov.cn/bcms/front/s39/c1869/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zsjg_gg", "http://www.yuanjiang.gov.cn/bcms/front/s39/c1871/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg", "http://www.yuanjiang.gov.cn/bcms/front/s39/c1872/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://www.yuanjiang.gov.cn/bcms/front/s39/c1873/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://www.yuanjiang.gov.cn/bcms/front/s39/c1876/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["yiliao_zhongbiao_gg", "http://www.yuanjiang.gov.cn/bcms/front/s39/c1885/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["yiliao_zhaobiao_gg", "http://www.yuanjiang.gov.cn/bcms/front/s39/c1883/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖南省沅江市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.4.175", "hunan", "yuanjiang"], pageloadtimeout=60, pageloadstrategy='none')
