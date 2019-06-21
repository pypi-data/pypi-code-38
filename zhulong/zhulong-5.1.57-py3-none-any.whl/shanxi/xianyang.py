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
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs


_name_="xianyang"



def f1(driver, num):
    locator = (By.XPATH, '//div[@class="isoc_dynamic-right fr"]/ul/li[1]/div/h3/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//div[@class="pagesite"]')
    str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = re.findall(r'(\d+)/', str)[0]
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath('//div[@class="isoc_dynamic-right fr"]/ul/li[1]/div/h3/a').get_attribute('href')[-10:]
        if "index.jhtml" in url:
            s = "index_%d.jhtml" % (num) if num > 1 else "index_1.jhtml"
            url = re.sub("index\.jhtml", s, url)
        elif num == 1:
            url = re.sub("index_[0-9]*", "index_1", url)
        else:
            s = "index_%d" % (num) if num > 1 else "index_1"
            url = re.sub("index_[0-9]*", s, url)
        driver.get(url)
        locator = (By.XPATH, "//div[@class='isoc_dynamic-right fr']/ul/li[1]/div/h3/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("div", class_='isoc_dynamic-right fr')
    ul = table.find("ul")
    trs = ul.find_all("li")
    data = []
    for tr in trs:
        a = tr.find("a")
        try:
            title = a["title"].strip()
        except:
            title = a.text.strip()
        try:
            link = a["href"]
        except:
            link = '-'
        span = tr.find('span').text.strip()
        span = re.findall(r'\((.*)\)', span)[0]
        links = link.strip()
        tmp = [title, span, links]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="isoc_dynamic-right fr"]/ul/li[1]/div/h3/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//div[@class="pagesite"]')
    str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'/(\d+)', str)[0]
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='newsTex'][string-length()>40] | //div[@class='newsTexNew'][string-length()>40]")
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
    div = soup.find('div', class_="newsTexNew")
    if div == None:
        div = soup.find('div', class_="newsTex")
    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://www.xyzhb.com/zbgg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg",
     "http://www.xyzhb.com/zhbgg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp,**args):
    est_meta(conp,data=data,diqu="陕西省咸阳市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shanxi","xianyang"])


