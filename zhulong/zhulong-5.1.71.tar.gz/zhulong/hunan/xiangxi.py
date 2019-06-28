import json

import pandas as pd
import re
import sys
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write, db_command, db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from lxml import etree
from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, add_info

_name_ = "xiangxi"


def f1(driver, num):
    locator = (By.XPATH, '//div[@id="static"]/ul/li[1]/div/a')
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-40:]
    locator = (By.XPATH, "//li[@class='ewb-page-li current']")
    try:
        cnum = int(WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text)
    except:cnum = 1
    if cnum != num:

        url = re.sub("\/[\d\w]+?\.html", '/%s.html'%str(num) , driver.current_url)
        driver.get(url)
        locator = (By.XPATH, "//div[@id='static']/ul/li[1]/div/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source

    body = etree.HTML(page)

    contents = body.xpath('//div[@id="static"]/ul/li')
    data = []
    for content in contents:

        name = re.sub('<[^>]+?>','',content.xpath('./div/a/@title')[0].strip())

        href = 'http://ggzyjy.xxz.gov.cn' + content.xpath('./div/a/@href')[0].strip()
        ggstart_time = content.xpath('./span/text()')[0].strip()

        tmp = [name,href,ggstart_time]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    try:
        locator = (By.XPATH, '//*[@id="static"]/div/ul/li[last()-3]/a')
        total_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    except:total_page = 1
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)

    locator = (By.CLASS_NAME, "imp")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

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

    div = soup.find('div', class_='imp')

    return div


data = [
    ["gcjs_zhaobiao_gg", "http://ggzyjy.xxz.gov.cn/jyxx/005001/005001001/aboutjyxxsearch.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_gqita_buchong_gg", "http://ggzyjy.xxz.gov.cn/jyxx/005001/005001002/aboutjyxxsearch.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_dayi_gg", "http://ggzyjy.xxz.gov.cn/jyxx/005001/005001003/aboutjyxxsearch.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg", "http://ggzyjy.xxz.gov.cn/jyxx/005001/005001004/aboutjyxxsearch.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://ggzyjy.xxz.gov.cn/jyxx/005002/005002001/aboutjyxxsearch.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_gqita_buchong_gg", "http://ggzyjy.xxz.gov.cn/jyxx/005002/005002002/aboutjyxxsearch.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_dayi_gg", "http://ggzyjy.xxz.gov.cn/jyxx/005002/005002003/aboutjyxxsearch.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_gqita_liu_cheng_zhong_gg", "http://ggzyjy.xxz.gov.cn/jyxx/005002/005002004/aboutjyxxsearch.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_hetong_gg", "http://ggzyjy.xxz.gov.cn/jyxx/005002/005002005/aboutjyxxsearch.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["yiliao_zhaobiao_gg", "http://ggzyjy.xxz.gov.cn/jyxx/005003/005003001/aboutjyxxsearch.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["yiliao_gqita_buchong_gg", "http://ggzyjy.xxz.gov.cn/jyxx/005003/005003002/aboutjyxxsearch.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["yiliao_gqita_zhong_liu_gg", "http://ggzyjy.xxz.gov.cn/jyxx/005003/005003004/aboutjyxxsearch.html", ["name", "href", "ggstart_time", "info"], f1, f2],

    ["yiliao_hetong_gg", "http://ggzyjy.xxz.gov.cn/jyxx/005003/005003005/aboutjyxxsearch.html", ["name", "href", "ggstart_time", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖南省湘西自治区", **args)

    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    conp = ['postgres','since2015','192.168.3.171','hunan','xiangxi']
    work(conp,headless=False,num=1)
    # url = "ggzyjy.xxz.gov.cn/ "
    # for d in data:
    #     url = d[1]
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #     f1(driver,3)
    #     f1(driver,5)
    #     print(f3(driver, 'http://ggzyjy.xxz.gov.cn/jyxx/005003/005003005/20190428/2763e692-4e91-47ff-a3fe-b12a92a10c7c.html'))
    #     driver.get(url)
    #     print(f2(driver))
