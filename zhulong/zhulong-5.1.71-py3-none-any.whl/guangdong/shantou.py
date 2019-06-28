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
from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, add_info, est_gg

# driver=webdriver.Chrome()
# url="http://www.bygzjy.cn/f/trade/annogoods/list?selectedProjectType=3"
# driver.get(url)

_name_ = 'shantou'


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="con-right fr"]/div[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url=driver.current_url

    if 'list.shtml' in url:
        cnum =1
    else:
        cnum=int(re.findall('list_(\d+).shtml',url)[0])


    if cnum != num:
        val = driver.find_element_by_xpath(
            '//div[@class="con-right fr"]/div[1]//a').get_attribute('href')[-30:-5]

        url=re.sub('list_{0,1}\d*.shtml','list_%s.shtml'%num,url) if num != 1 else re.sub('list_\d+.shtml','list.shtml',url)

        driver.get(url)

        locator = (
            By.XPATH, "//div[@class='con-right fr']/div[1]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("div", class_="con-right fr")
    dls = div.find_all("div",recursive=False)[:-1]

    data = []
    for dl in dls:

        name = dl.find('a').get_text()
        href = dl.find('a')['href']
        ggstart_time = dl.find('td',align='left').get_text()
        ggstart_time=re.findall('\d+-\d+-\d+',ggstart_time)[0]
        info = None

        if 'http' in href:
            href = href
        else:
            href = 'http://www.shantou.gov.cn' + href

        tmp = [name, ggstart_time, href, info]

        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="con-right fr"]/div[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    html=driver.page_source
    total=re.findall("createPageHTML\('page_div',(\d+?),",html)[0]

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@id="zoomcon"][string-length()>50]')
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
    div = soup.find('div', class_='main')

    return div


data = [

    ["gcjs_zhaobiao_gg",
     "http://www.shantou.gov.cn/ggzyjy/jsbggg/list.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_biangeng_gg",
     "http://www.shantou.gov.cn/ggzyjy/jszbgga/list.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.shantou.gov.cn/ggzyjy/jszbgs/list.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://www.shantou.gov.cn/ggzyjy/jszbgg/list.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["zfcg_zhaobiao_gg",
     "http://www.shantou.gov.cn/ggzyjy/zfzbgg/list.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://www.shantou.gov.cn/ggzyjy/zfbggg/list.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiaohx_gg",
     "http://www.shantou.gov.cn/ggzyjy/zfyzbgga/list.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://www.shantou.gov.cn/ggzyjy/zfzbgga/list.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省汕头市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(
        conp=[
            "postgres",
            "since2015",
            '192.168.3.171',
            "guangdong",
            "shantou"],
        headless=True,
        num=1,
        total=2)
