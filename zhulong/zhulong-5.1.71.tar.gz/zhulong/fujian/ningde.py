from os.path import join, dirname
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
from zhulong.util.etl import add_info, est_meta, est_html, est_tbs, gg_existed
from zhulong.util.conf import get_conp

_name_="ningde"



def zfcg_data(driver, num):
    url = driver.current_url
    locator = (By.XPATH, "//table[@class='table table-hover dataTables-example']/tbody/tr[1]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//button[@class='active']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        cnum = int(st)
    except:
        cnum = 1
    try:
        notice_type = re.findall(r'notice_type=(.*)&', url)[0]
    except:
        notice_type = re.findall(r'notice_type=(.*)', url)[0]

    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@class='table table-hover dataTables-example']/tbody/tr[1]/td/a").get_attribute("href")[-30:]
        driver.execute_script("javascript:location.href='?page={0}&notice_type={1}'".format(num, notice_type))
        # driver.execute_script("javascript:location.href='?page=6&notice_type=7dc00df822464bedbf9e59d02702b714'")
        try:
            locator = (By.XPATH,
                       "//table[@class='table table-hover dataTables-example']/tbody/tr[1]/td/a[not(contains(@href,'%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            driver.refresh()
            locator = (By.XPATH,
                       "//table[@class='table table-hover dataTables-example']/tbody/tr[1]/td/a[not(contains(@href,'%s'))]" % val)
            WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", class_="table table-hover dataTables-example")
    tbody = table.find('tbody')
    trs = tbody.find_all("tr", class_="gradeX")
    data = []
    for tr in trs:
        a = tr.find('a')
        try:
            title = a["title"].strip()
        except:
            title = a.text.strip()
        td = tr.find_all("td")[-1].text.strip()
        link = "http://zfcg.czj.ningde.gov.cn/" + a["href"].strip()
        diqu = tr.find_all("td")[0].text.strip()
        cgfs = tr.find_all("td")[1].text.strip()
        cgdw = tr.find_all("td")[2].text.strip()
        dd ={'diqu':diqu, 'cgfs':cgfs, 'cgdw':cgdw}
        info = json.dumps(dd, ensure_ascii=False)
        tmp = [title, td, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f1(driver, num):
    url = driver.current_url
    if "http://zfcg.czj.ningde.gov.cn/350900/noticelist/" in url:
        df = zfcg_data(driver, num)
        return df
    locator = (By.XPATH, "//div[@class='gl_right']/div/div[1]/ul/li[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//a[@class='cur']")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        cnum = 1

    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='gl_right']/div/div[1]/ul/li[1]/a").get_attribute('href')[-20:]

        locator = (By.XPATH, "//div[@avalonctrl='list_pagebar']/input[@type='text']")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        locator = (By.XPATH, "//div[@avalonctrl='list_pagebar']/input[@type='text']")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).clear()
        locator = (By.XPATH, "//div[@avalonctrl='list_pagebar']/input[@type='text']")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).send_keys(num)
        locator = (By.XPATH, "//div[@avalonctrl='list_pagebar']/button")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        try:
            locator = (By.XPATH, "//div[@class='gl_right']/div/div[1]/ul/li[1]/a[not(contains(@href,'%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            driver.refresh()
            locator = (By.XPATH, "//div[@class='gl_right']/div/div[1]/ul/li[1]/a[not(contains(@href,'%s'))]" % val)
            WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("div", class_="gl_right")
    divs = table.find_all('div', class_='gl_lb')
    data = []
    for div in divs:
        ul = div.find('ul', class_='list')
        lis = ul.find_all('li')
        for li in lis:
            a = li.find('a')
            try:
                title = a["title"].strip()
            except:
                title = a.text.strip()
            href = a["href"]
            if 'http' in href:
                link = href.strip()
            else:
                link = url + href.split('/', maxsplit=1)[1]
            td = li.find("span").text.strip()
            tmp = [title, td, link]
            data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f2(driver):
    url = driver.current_url
    if "http://zfcg.czj.ningde.gov.cn/" in url:
        locator = (By.XPATH, "//button[@class='active']")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        locator = (By.XPATH, "//div[@class='pageGroup']/button[last()]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        try:
            locator = (By.XPATH, "//button[@class='active'][not(contains(string(),'%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            locator = (By.XPATH, "//button[@class='active']")
            st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num = int(st)
        except:
            num = 1
        driver.quit()
        return int(num)
    else:
        locator = (By.XPATH, "//div[@class='gl_right']/div/div[1]/ul/li[1]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, "//div[@avalonctrl='list_pagebar']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = re.findall(r'共(\d+)页', st)[0]
        driver.quit()
        return int(num)


def f3(driver, url):
    driver.get(url)
    if "http://zfcg.czj.ningde.gov.cn/" in url:
        locator = (By.XPATH, "//div[@id='print-content'][string-length()>200]")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        locator = (By.XPATH, "//div[@class='notice-con'][string-length()>100]")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        before = len(driver.page_source)
        time.sleep(0.5)
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
        div = soup.find('div', id="print-content")
        return div
    locator = (By.XPATH, "//div[@class='xl_main'][string-length()>200]")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    before = len(driver.page_source)
    time.sleep(0.5)
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
    div = soup.find('div', class_="xl_main")
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.ningde.gov.cn/ztzl/ndsggzyjyzx/gcjs_20226/zbgg_20227/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_bian_da_gg",
     "http://www.ningde.gov.cn/ztzl/ndsggzyjyzx/gcjs_20226/dygg_20228/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.ningde.gov.cn/ztzl/ndsggzyjyzx/gcjs_20226/zbhxrgs_20229/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://www.ningde.gov.cn/ztzl/ndsggzyjyzx/gcjs_20226/zbjggs_20230/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://zfcg.czj.ningde.gov.cn/350900/noticelist/d03180adb4de41acbb063875889f9af1/?zone_code=&zone_name=&croporgan_name=&project_no=&fromtime=&endtime=&gpmethod=&agency_name=&title=&notice_type=463fa57862ea4cc79232158f5ed02d03&purchase_item_name=",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_biangeng_gg",
     "http://zfcg.czj.ningde.gov.cn/350900/noticelist/d03180adb4de41acbb063875889f9af1/?page=1&notice_type=7dc00df822464bedbf9e59d02702b714&",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://zfcg.czj.ningde.gov.cn/350900/noticelist/d03180adb4de41acbb063875889f9af1/?page=21&notice_type=b716da75fe8d4e4387f5a8c72ac2a937&",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_jieguo_gg",
     "http://zfcg.czj.ningde.gov.cn/350900/noticelist/d03180adb4de41acbb063875889f9af1/?zone_code=&zone_name=&croporgan_name=&project_no=&fromtime=&endtime=&gpmethod=&agency_name=&title=&notice_type=d812e46569204c7fbd24cbe9866d0651&purchase_item_name=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_danyilaiyuan_gg",
     "http://zfcg.czj.ningde.gov.cn/350900/noticelist/d03180adb4de41acbb063875889f9af1/?zone_code=&zone_name=&croporgan_name=&project_no=&fromtime=&endtime=&gpmethod=&agency_name=&title=&notice_type=255e087cf55a42139a1f1b176b244ebb&purchase_item_name=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"zbfs":"单一来源"}), f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="福建省宁德市",**args)
    est_html(conp,f=f3,**args)



if __name__=='__main__':
    work(conp=["postgres","zhulong.com.cn","192.168.169.47","fujian","ningde"],pageloadtimeout=180, pageloadstrategy="none",num=1,headless=False)


