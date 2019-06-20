import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_command,db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, NoAlertPresentException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import json
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs


_name_="mianyang2"



def f1(driver, num):
    url = driver.current_url
    locator = (By.XPATH, "//div[@class='article_list']//tbody/tr[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//span[@id='index']")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = cnum.split('/')[0]
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='article_list']//tbody/tr[1]//a").get_attribute('href')[-30:]
        if "lists.html"in url:
            s = "%d.html" % (num) if num > 1 else "lists.html"
            url = re.sub("lists\.html", s, url)
        elif num == 1:
            url = re.sub("[0-9]*\.html", "lists.html", url)
        else:
            s = "%d.html" % (num) if num > 1 else "lists.html"
            url = re.sub("[0-9]*\.html", s, url)
        driver.get(url)
        locator = (By.XPATH, "//div[@class='article_list']//tbody/tr[1]//a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("div", class_="article_list")
    tbody = table.find('tbody')
    trs = tbody.find_all("tr")
    data = []
    for tr in trs:
        a = tr.find('a')
        link = "http://ggjy.my.gov.cn:8000" + a['href'].strip()
        td = tr.find("span", class_="dt").text.strip()
        try:
            font = a.find_all('font')
            if int(len(font)) > 1:
                gclx = a.find_all('font')[0].extract().text.strip()
                gclx = re.findall(r'\[(.*)\]', gclx)[0]
                a.find_all('font')[0].extract().text.strip()
                info = {'gclx': gclx}
            else:
                gclx = a.find_all('font')[0].extract().text.strip()
                gclx = re.findall(r'\[(.*)\]', gclx)[0]
                info = {'gclx': gclx}
            info = json.dumps(info, ensure_ascii=False)
        except:
            info = None

        title = a.text.strip()
        if re.findall(r'\[(.*?)\]$', title):
            title = re.findall(r'(.*)\[.*\]$', title)[0]

        tmp = [title, td, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='article_list']//tbody/tr[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        driver.find_element_by_xpath("(//li[@class='wb-page-li wb-page-item ']/a)[last()]").click()
        locator = (By.XPATH, "//span[@id='index']")
        num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = num.split('/')[1]
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    if re.findall(r'\.pdf$', url):
        return url
    locator = (By.XPATH, "//div[@id='content'] | //div[@id='article']")
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
    div = soup.find('div', id="content")
    if div == None:
        div = soup.find('div', id='article')
    return div



data = [
    ["gcjs_zhaobiao_gg",
     "http://ggjy.my.gov.cn:8000/jsgc/001001/lists.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://ggjy.my.gov.cn:8000/jsgc/001003/lists.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zsjg_gg",
     "http://ggjy.my.gov.cn:8000/jsgc/001004/lists.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://ggjy.my.gov.cn:8000/jsgc/001005/lists.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_zhonghxbiangeng_gg",
     "http://ggjy.my.gov.cn:8000/jsgc/001006/lists.html",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gglx':'中标候选人公示变更'}),f2],

    ["gcjs_gqita_liu_zhongz_gg",
     "http://ggjy.my.gov.cn:8000/jsgc/001007/lists.html",
     ["name", "ggstart_time", "href", "info"], f1,f2],

    ["gcjs_zhongbiao_gg",
     "http://ggjy.my.gov.cn:8000/jsgc/001008/lists.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_hetong_gg",
     "http://ggjy.my.gov.cn:8000/jsgc/001009/lists.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_gg",
     "http://ggjy.my.gov.cn:8000/jsgc/001012/lists.html",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gglx':'其他公示'}), f2],
]



def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省绵阳市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","sichuan","mianyang2"])



