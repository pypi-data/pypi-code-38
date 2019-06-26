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


_name_="jiaxing"


def f1_data(driver, num):
    locator = (By.XPATH, "(//div[@class='newscontentleft']/a)[1]")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-20:]
    locator = (By.XPATH, "(//div[@id='pages']/font)[2]")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = re.findall(r'[0-9]+', st)[0]
    url = driver.current_url
    if num != int(cnum):
        if num == 1:
            url = re.sub("pageNow=[0-9]*", "pageNow=1", url)
        else:
            s = "pageNow=%d" % (num) if num > 1 else "pageNow=1"
            url = re.sub("pageNow=[0-9]*", s, url)
        driver.get(url)
        locator = (By.XPATH, "(//div[@class='newscontentleft']/a)[1][not(contains(@href, '%s'))]".format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("div", class_='newscontent')
    ul = div.find("ul")
    trs = ul.find_all("li")
    data = []
    for tr in trs:
        a = tr.find("a")
        link = a["href"]
        td = tr.find("div", class_="newscontentright").text
        tmp = [a.text.strip(), td.strip(), "http://www.zjyxcg.cn" + link.strip()]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f1(driver, num):
    url = driver.current_url
    if 'http://www.zjyxcg.cn/' in url:
        df = f1_data(driver, num)
        return df
    locator = (By.XPATH, "(//div[@class='wb-data-infor']/a)[1]")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-30:]

    locator = (By.XPATH, "//li[@class='ewb-page-li current']")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    if num != int(cnum):
        if num == 1:
            url = re.sub("/[0-9]*\.html", "/subpagesecond.html", url)
        else:
            s = "/%d.html" % (num) if num > 1 else "/1.html"
            if "subpagesecond" in url:
                url = re.sub("/subpagesecond\.html", s, url)
            else:
                url = re.sub("/[0-9]*\.html", s, url)
        driver.get(url)
        locator = (By.XPATH, "(//div[@class='wb-data-infor']/a)[1][not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    ul = soup.find("ul", class_='wb-data-item center')
    trs = ul.find_all("li", class_="wb-data-list")
    data = []
    for tr in trs:
        a = tr.find("a")
        link = a["href"]
        td = tr.find("span", class_="wb-data-date").text
        tmp = [a["title"].strip(), td.strip(), "http://www.jxzbtb.cn" + link.strip()]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f2(driver):
    url = driver.current_url
    if 'http://www.zjyxcg.cn/' in url:
        locator = (By.XPATH, "(//div[@class='newscontentleft']/a)[1]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, "(//div[@id='pages']/font)[1]")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        num = re.findall(r'[0-9]+', st)[0]
    else:
        locator = (By.XPATH, "(//div[@class='wb-data-infor']/a)[1]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            cnum = 0
            while True:
                cnum += 1
                locator = (By.XPATH, "(//div[@class='wb-data-infor']/a)[1]")
                val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-30:]
                locator = (By.XPATH, "//li[@class='ewb-page-li ewb-page-hover'][2]/a")
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
                locator = (By.XPATH, "(//div[@class='wb-data-infor']/a)[1][not(contains(@href, '%s'))]" % val)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
                if "404" in driver.title:
                    break
        except:
            try:
                locator = (By.XPATH, "//li[@class='ewb-page-li current']")
                cn = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
                num = int(cn)
            except:
                num = cnum - 1

    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    if '404' in driver.title:
        return 404
    if 'http://www.zjyxcg.cn/' in url:
        locator = (By.XPATH, "//div[@id='conextId']")
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
        div = soup.find('div', id='conextId')
        return div
    else:
        locator = (By.XPATH, "//div[@class='ewb-info-list'][string-length()>40]")
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
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
        div = soup.find('div', class_='ewb-info-list')
        return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.jxzbtb.cn/jygg/003001/003001001/subpagesecond.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.jxzbtb.cn/jygg/003001/003001004/subpagesecond.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiao_gg",
     "http://www.jxzbtb.cn/jygg/003001/003001005/subpagesecond.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_bian_zhongz_gg",
     "http://www.jxzbtb.cn/jygg/003001/003001006/subpagesecond.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhaobiao_gg",
     "http://www.jxzbtb.cn/jygg/003002/003002001/subpagesecond.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhongbiao_gg",
     "http://www.jxzbtb.cn/jygg/003002/003002002/subpagesecond.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_gqita_bian_da_gg",
     "http://www.jxzbtb.cn/jygg/003002/003002003/subpagesecond.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_zhaobiao_gg",
     "http://www.jxzbtb.cn/jygg/003007/003007001/subpagesecond.html",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'镇街道部门国资公司'}),f2],

    ["qsy_zhongbiao_gg",
     "http://www.jxzbtb.cn/jygg/003007/003007003/subpagesecond.html",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'镇街道部门国资公司'}),f2],

    ["jqita_zhaobiao_gg",
     "http://www.jxzbtb.cn/jygg/003008/003008001/subpagesecond.html",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'其他公共资源交易'}),f2],

    ["jqita_zhongbiao_gg",
     "http://www.jxzbtb.cn/jygg/003008/003008002/subpagesecond.html",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'其他公共资源交易'}),f2],

    ["yiliao_gqita_yaopincaigou_gg",
     "http://www.zjyxcg.cn/showListZCFG.html?catalogId=3&type=1&pageNow=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'药品采购'}),f2],

    ["yiliao_gqita_haocaicaigou_gg",
     "http://www.zjyxcg.cn/showListZCFG.html?catalogId=3&type=2&pageNow=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'耗材采购'}),f2],

    ["yiliao_gqita_zonghe_gg",
     "http://www.zjyxcg.cn/showListZCFG.html?catalogId=3&type=3&pageNow=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'综合业务'}),f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="浙江省嘉兴市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","zhejiang","jiaxing"])

