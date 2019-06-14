import json

from collections import OrderedDict
from pprint import pprint

import pandas as pd
import re

import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write, db_command, db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, add_info, est_gg

# driver=webdriver.Chrome()
# url="http://www.bygzjy.cn/f/trade/annogoods/list?selectedProjectType=3"
# driver.get(url)

_name_ = 'zhixiashi_shanghai'


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="Article"]/iframe')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    ifra=driver.find_element_by_xpath('//div[@class="Article"]/iframe')
    driver.switch_to.frame(ifra)

    locator = (By.XPATH, '(//div[@align="center"]/table/tbody/tr/td/table[3]//tr[2]//a)[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath('//input[@id="hdInputNum"]').get_attribute('value')

    if int(cnum) != num:
        val = driver.find_element_by_xpath(
            '(//div[@align="center"]/table/tbody/tr/td/table[3]//tr[2]//a)[1]').get_attribute('onclick')
        val = re.findall("openWindow\('(.+?)','.+?'\)", val)[0]
        sele=driver.find_element_by_xpath('//select[@id="DropDownList_page"]')
        sele=Select(sele)
        sele.select_by_value(str(num))
        time.sleep(0.1)
        driver.find_element_by_xpath('//input[@id="lkGoto"]').click()

        locator = (
            By.XPATH, "(//div[@align='center']/table/tbody/tr/td/table[3]//tr[2]//a)[1][not(contains(@onclick,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    dls = soup.find_all("tr",style="border-bottom: black solid; border-bottom-width: 1px; font-size: 12px;")

    data = []
    for dl in dls:
        tds = dl.find_all('td')
        try:
            name = dl.find('a').get_text().strip()
            href = dl.find('a')['onclick']
            ggstart_time = tds[-2].get_text().strip()
            ggtype=tds[-1].get_text().strip()
            vercontrol=re.findall("openWindow\('.+?','(.+?)'\)",href)[0]
            xh=re.findall("openWindow\('(.+?)','.+?'\)",href)[0]
            if vercontrol == "v2_jypt":
                href = 'https://www.ciac.sh.cn/NetInterBidweb/GKTB/DefaultV2017.aspx?gkzbXh=' + xh
            else:
                href = 'https://www.ciac.sh.cn/NetInterBidweb/GKTB/DefaultV2011.aspx?gkzbXh='+ xh

            info=json.dumps({'ggtype':ggtype},ensure_ascii=False)

            tmp = [name, ggstart_time, href, info]

            data.append(tmp)
        except:
            pass
    df = pd.DataFrame(data=data)

    driver.switch_to.parent_frame()
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="Article"]/iframe')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    ifra = driver.find_element_by_xpath('//div[@class="Article"]/iframe')
    driver.switch_to.frame(ifra)

    locator = (By.XPATH, '(//div[@align="center"]/table/tbody/tr/td/table[3]//tr[2]//a)[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total=driver.find_element_by_xpath('//input[@id="lastPage"]').get_attribute('title')

    driver.quit()
    return int(total)




def f4(driver, num):
    locator = (By.XPATH, '//div[@class="Article"]/iframe')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    ifra=driver.find_element_by_xpath('//div[@class="Article"]/iframe')
    driver.switch_to.frame(ifra)

    locator = (By.XPATH, '//table[@id="gvList"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath('//tr[@class="pagestyle"]//span').text

    if int(cnum) != num:
        val = driver.find_element_by_xpath(
            '//table[@id="gvList"]//tr[2]//a').get_attribute('onclick')

        val = re.findall('ShowGs\((.+?),"', val)[0]

        driver.execute_script("javascript:__doPostBack('gvList','Page$%s')"%num)

        locator = (
            By.XPATH, "//table[@id='gvList']//tr[2]//a[not(contains(@onclick,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div=soup.find('table',id='gvList')
    dls = div.find_all("tr",class_=False,recursive=False)

    data = []
    for dl in dls:
        tds = dl.find_all('td')

        name = dl.find('a').get_text().strip()
        href = dl.find('a')['onclick']
        ggstart_time = tds[-2].get_text().strip()
        ggtype=tds[-1].get_text().strip()
        id_=re.findall('ShowGs\((.*?),".*?",".*?"\)',href)[0]
        zblx=re.findall('ShowGs\(.*?,"(.*?)",".*?"\)',href)[0]
        zbgcid=re.findall('ShowGs\(.*?,".*?","(.*?)"\)',href)[0]

        if zbgcid != "" and zbgcid != None:
            href = "https://www.ciac.sh.cn/XMJYPTInterWeb/Tender/PrinttoPdf?zbgcid=" + zbgcid
        elif zblx != None and len(zblx) > 2 and zblx != "sgzgj":
            href = '错误'
        else:
            href = "http://www.ciac.sh.cn/XmZtbbaWeb/Gsqk/GsFb.aspx?zbid="+id_

        info=json.dumps({'ggtype':ggtype},ensure_ascii=False)

        tmp = [name, ggstart_time, href, info]

        data.append(tmp)

    df = pd.DataFrame(data=data)

    driver.switch_to.parent_frame()
    return df


def f6(driver, num):
    locator = (By.XPATH, '//div[@class="Article"]/iframe')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    ifra = driver.find_element_by_xpath('//div[@class="Article"]/iframe')
    driver.switch_to.frame(ifra)

    locator = (By.XPATH, '//table[@id="gvZbjgGkList"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath('//tr[@class="pagestyle"]//span').text

    if int(cnum) != num:
        val = driver.find_element_by_xpath(
            '//table[@id="gvZbjgGkList"]//tr[2]//a').get_attribute('href')

        val = re.findall("javascript:__doPostBack\('(.+?)'", val)[0]

        driver.execute_script("javascript:__doPostBack('gvZbjgGkList','Page$%s')" % num)

        locator = (
            By.XPATH, "//table[@id='gvZbjgGkList']//tr[2]//a[not(contains(@onclick,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    VIEWSTATEGENERATOR = driver.find_element_by_xpath('//input[@id="__VIEWSTATEGENERATOR"]').get_attribute('value')
    EVENTVALIDATION = driver.find_element_by_xpath('//input[@id="__EVENTVALIDATION"]').get_attribute('value')
    VIEWSTATE = driver.find_element_by_xpath('//input[@id="__VIEWSTATE"]').get_attribute('value')

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('table', id='gvZbjgGkList').find('tbody')
    dls = div.find_all("tr", class_=False, recursive=False)

    data = []
    for dl in dls:

        tds = dl.find_all('td')

        name = dl.find('a').get_text().strip()
        href = dl.find('a')['href']
        ggstart_time = tds[-2].get_text().strip()
        ggtype = tds[-1].get_text().strip()

        EVENTTARGET = re.findall("javascript:__doPostBack\('(.+?)'", href)[0]

        form_data = {

            "__EVENTTARGET": EVENTTARGET,
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": VIEWSTATE,
            "__VIEWSTATEGENERATOR": VIEWSTATEGENERATOR,
            "__EVENTVALIDATION": EVENTVALIDATION,
            "ddlZblx": "",
            "txtZbrqBegin": "",
            "txtZbrqEnd": "",
            "txtZbr": "",
        }
        req_url = 'https://www.ciac.sh.cn/XmZtbbaWeb/gsqk/ZbjgGkList.aspx'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        }
        req = requests.post(req_url, data=form_data, headers=headers, allow_redirects=False)

        if int(str(req.status_code)[0]) != 3:
            raise ConnectionError('response status code is %s' % req.status_code)

        href = req.headers['Location']
        if 'http' in href:
            href = href
        else:
            href = 'https://www.ciac.sh.cn' + href

        info = json.dumps({'ggtype': ggtype}, ensure_ascii=False)

        tmp = [name, ggstart_time, href, info]

        data.append(tmp)

    driver.switch_to.parent_frame()

    df = pd.DataFrame(data=data)
    return df



def f5(driver):
    locator = (By.XPATH, '//div[@class="Article"]/iframe')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    ifra = driver.find_element_by_xpath('//div[@class="Article"]/iframe')
    driver.switch_to.frame(ifra)

    locator = (By.XPATH, '//table[@id="gvList"]//tr[2]//a | //table[@id="gvZbjgGkList"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath('//tr[@class="pagestyle"]//td[last()]/a').text

    driver.quit()
    return int(total)




def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//body[string-length()>100]')
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
    div = soup.find('body')

    return div




data=[

    ["gcjs_zhaobiao_gg" , 'http://www.shcpe.cn/jyfw/xxfw/u1ai17.html', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["gcjs_zhongbiaohx_gg" , 'http://www.shcpe.cn/jyfw/xxfw/u1ai18.html', ["name", "ggstart_time", "href", 'info'],f4, f5],
    ["gcjs_zhongbiao_gg" , 'http://www.shcpe.cn/jyfw/xxfw/u1ai51.html', ["name", "ggstart_time", "href", 'info'],f6, f5],

      ]

# pprint(data)


def work(conp, **args):
    est_meta(conp, data=data, diqu="上海市", **args)
    # est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(
        conp=[
            "postgres",
            "since2015",
            '192.168.3.171',
            "zhixiashi",
            "shanghai"],
        headless=True,
        num=1,
    )
    pass