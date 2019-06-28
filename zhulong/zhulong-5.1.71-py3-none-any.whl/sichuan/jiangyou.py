import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_command,db_query
from selenium.webdriver import DesiredCapabilities
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


_name_="jiangyou"





def f1(driver, num):
    locator = (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_myGV_ctl02_HLinkGcmc"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, '//tr[@class="myGVPagerCss"]/td/span[1]')
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(st)
        j = 0
    except:
        cnum = 1
        j = 1
    if num != int(cnum):
        if num > int(cnum):
            t = num - int(cnum)
            for i in range(t):
                locator = (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_myGV_ctl02_HLinkGcmc"]')
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
                driver.find_element_by_link_text('下一页').click()

            locator = (By.XPATH, '//tr[@class="myGVPagerCss"]/td/span[1]')
            cnum_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            if num != int(cnum_1):
                raise TimeoutError

        if num < int(cnum):
            t = int(cnum) - num
            for i in range(t):
                locator = (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_myGV_ctl02_HLinkGcmc"]')
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
                driver.find_element_by_link_text('上一页').click()

            locator = (By.XPATH, '//tr[@class="myGVPagerCss"]/td/span[1]')
            cnum_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            if num != int(cnum_1):
                raise TimeoutError

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", id='ctl00_ContentPlaceHolder1_myGV')
    trs = table.find_all("tr")
    data = []
    i = -1
    if j ==1:
        i = None
    url = driver.current_url
    for tr in trs[1:i]:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        try:
            href = a['href'].strip()
            if "http" in href:
                link = href
            else:
                link = "http://jyggzy.my.gov.cn/ceinwz/" + href
        except:
            link = '-'
        try:
            td = tr.find("td", class_="fFbDate")
            span = td.find('span').text.strip()
        except:
            span = '-'
        try:
            title = re.sub(r'\[(.*)\]', '', title).strip()
            if '※' in title:
                title = re.sub(r'※', '', title).strip()
        except:
            if '※' in title:
                title = re.sub(r'※', '', title).strip()
            title = title
        tmp = [title, span, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_myGV_ctl02_HLinkGcmc"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_myGV_ctl23_LabelPageCount"]')
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = int(st)
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    url = driver.current_url
    if '/ceinwz/admin_show.aspx' in url:
        locator = (By.XPATH, "//span[@id='ctl00_ContentPlaceHolder1_BodyLabel'][string-length()>30]")
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
        div = soup.find('span', id="ctl00_ContentPlaceHolder1_BodyLabel")
        return div
    else:
        if 'id="frmBestwordHtml"' in str(driver.page_source):
            driver.switch_to_frame('frmBestwordHtml')
            locator = (By.XPATH, "//div[contains(@class, 'Section')][string-length()>30]")
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        else:
            locator = (By.XPATH, "//table[@width='75%'][string-length()>30]")
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
        div = soup.find('div', class_=re.compile(r'.*?Section.*?'))
        if div == None:
            div = soup.find('table', width="75%")
        return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://jyggzy.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=100&jsgc=0100000&zfcg=&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=jsgc",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://jyggzy.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=101&jsgc=0010000&zfcg=&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=jsgc",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://jyggzy.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=102&jsgc=0000010&zfcg=&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=jsgc",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhaobiao_gg",
     "http://jyggzy.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=201&jsgc=&zfcg=0100000&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=zfcg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_bian_bu_gg",
     "http://jyggzy.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=202&jsgc=&zfcg=0010000&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=zfcg",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_gqita_zhong_liu_gg",
     "http://jyggzy.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=203&jsgc=&zfcg=0000001&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=zfcg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_yucai_gg",
     "http://jyggzy.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=200&jsgc=&zfcg=0000100&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=zfcg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]



def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省江油市",**args)
    est_html(conp,f=f3,**args)

# 修改时间：2019/6/27
if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","sichuan","jiangyou"],pageloadtimeout=60)





