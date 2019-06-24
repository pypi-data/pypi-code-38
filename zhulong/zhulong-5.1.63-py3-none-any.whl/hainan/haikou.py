import json
import random
import time
import pandas as pd
import re
import requests
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs

_name_="haikou"


def zb_gg(f):
    def warp(*krg):
        driver=krg[0]
        locator = (By.XPATH, '//li[@class="active"]')
        val_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if val_1 != '招标公告':
            locator = (By.XPATH, '//ul[@class="secNav_ul"]//li[text()="招标公告"]')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            locator = (By.XPATH, '//li[@class="active"][text()="招标公告"]')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*krg)
    return warp

def zbhx_gg(f):
    def warp(*krg):
        driver=krg[0]
        locator = (By.XPATH, '//li[@class="active"]')
        val_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if val_1 != '中标候选人公示':
            locator = (By.XPATH, '//ul[@class="secNav_ul"]//li[text()="中标候选人公示"]')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            locator = (By.XPATH, '//li[@class="active"][text()="中标候选人公示"]')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*krg)
    return warp

def zbjg_gg(f):
    def warp(*krg):
        driver=krg[0]
        locator = (By.XPATH, '//li[@class="active"]')
        val_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if val_1 != '中标结果公告':
            locator = (By.XPATH, '//ul[@class="secNav_ul"]//li[text()="中标结果公告"]')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            locator = (By.XPATH, '//li[@class="active"][text()="中标结果公告"]')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*krg)
    return warp

def jy_gg(f):
    def warp(*krg):
        driver=krg[0]
        locator = (By.XPATH, '//li[@class="active"]')
        val_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if val_1 != '交易公告':
            locator = (By.XPATH, '//ul[@class="secNav_ul"]//li[text()="交易公告"]')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            locator = (By.XPATH, '//li[@class="active"][text()="交易公告"]')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*krg)
    return warp

def jg_gg(f):
    def warp(*krg):
        driver=krg[0]
        locator = (By.XPATH, '//li[@class="active"]')
        val_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if val_1 != '结果公告':
            locator = (By.XPATH, '//ul[@class="secNav_ul"]//li[text()="结果公告"]')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            locator = (By.XPATH, '//li[@class="active"][text()="结果公告"]')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*krg)
    return warp



def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='info_list']/li[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath("(//a[@class='link'])[last()]").text.strip()
    cnum = re.findall(r'(\d+)', total)[0]
    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='info_list']/li[last()]//a").get_attribute('onclick')[-30:-7]
        driver.execute_script("gotoPage({})".format(num))
        locator = (By.XPATH, "//ul[@class='info_list']/li[last()]//a[not(contains(@onclick, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    ul = soup.find('ul', class_='info_list')
    lis = ul.find_all('li')
    s = 0
    data = []
    for li in lis:
        s += 1
        a = li.find('a')
        info = {}
        if a.find('span'):
            gglx = a.find('span').extract().text.strip()
            if re.findall(r'(\w+)', gglx):
                gglx = re.findall(r'(\w+)', gglx)[0]
                info['gglx'] = gglx
        try:
            title = a['title']
        except:
            title = a.text.strip()
        js_tmp = """
            function detail(obj, keyid, attachment){
                var param = "flag="+flag;
                param += "&name="+type;
                param += "&key="+keyid;
                var url = path;
                if(flag==INDEX_JDXX || flag==INDEX_CXPT){
                    param += "&attachment="+attachment;
                    url += "/indexmain.do?method=showMoreInfo&param=";
                } else {
                    url += "/login.do?method=newDetail&param=";
                }
                var encode = encrypt(param);
                return url+encode;
            }
        """
        onclick = a['onclick']
        onclick = re.sub('this', "'{}'".format(title), onclick)
        js = js_tmp + """return {}""".format(onclick)
        link = driver.execute_script(js)
        href = 'http://ggzy.haikou.gov.cn' + link
        td = li.find('div', class_='col2').text.strip()
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:
            info = None
        tmp = [title, td, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, "//ul[@class='info_list']/li[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath("(//a[@class='link'])[last()]").text.strip()
    num = re.findall(r'(\d+)', total)[-1]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='content_wrap'][string-length()>30]")
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
    div = soup.find('div', class_="content_wrap")
    return div


data = [
    ["gcjs_zhaobiao_gg", "http://ggzy.haikou.gov.cn/login.do?method=newsecond&param=811241696e6465783d3326747970653d47435f4a59",
     ["name", "ggstart_time", "href", "info"], zb_gg(f1), zb_gg(f2)],

    ["gcjs_zhongbiaohx_gg", "http://ggzy.haikou.gov.cn/login.do?method=newsecond&param=811241696e6465783d3326747970653d47435f4a59",
     ["name", "ggstart_time", "href", "info"], zbhx_gg(f1), zbhx_gg(f2)],

    ["gcjs_zhongbiao_gg", "http://ggzy.haikou.gov.cn/login.do?method=newsecond&param=811241696e6465783d3326747970653d47435f4a59",
     ["name", "ggstart_time", "href", "info"], zbjg_gg(f1), zbjg_gg(f2)],

    ["zfcg_zhaobiao_gg", "http://ggzy.haikou.gov.cn/login.do?method=newsecond&param=811241696e6465783d3326747970653d47435f4a59",
     ["name", "ggstart_time", "href", "info"], jy_gg(f1), jy_gg(f2)],

    ["zfcg_gqita_zhong_liu_gg", "http://ggzy.haikou.gov.cn/login.do?method=newsecond&param=811241696e6465783d3326747970653d47435f4a59",
     ["name", "ggstart_time", "href", "info"], jg_gg(f1), jg_gg(f2)],
]


def work(conp,**args):
    est_meta(conp,data=data,diqu="海南省海口市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","hainan","haikou"],pageloadtimeout=60)

