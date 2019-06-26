
import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_command,db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

import json
from zhulong.util.etl import gg_meta,gg_html


# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]


# url="https://ggzy.changsha.gov.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type2"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

from zhulong.util.etl import add_info,est_meta,est_html,est_tbs


_name_="quanzhou"


def f1(driver, num):
    url = driver.current_url
    if ("/project/projectList.do?" in url) or ("/project/otherBidInfo.do?" in url):
        locator = (By.XPATH, "//dl[@id='LatestListPro']/table/tbody/tr[2]/td[2]/a")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-30:]
        try:
            locator = (By.XPATH, "//span[@id='pageIndex']")
            st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            cnum = int(st)
        except:
            cnum = 1
        if num != int(cnum):
            s1 = Select(driver.find_element_by_id('skipPage'))
            s1.select_by_value("{}".format(num))
            locator = (By.XPATH, "//dl[@id='LatestListPro']/table/tbody/tr[2]/td[2]/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        table = soup.find("dl", id="LatestListPro")
        trs = table.find_all("tr")
        data = []
        for tr in trs[1:]:
            a = tr.find('a')
            try:
                title = a["title"].strip()
            except:
                title = a.text.strip()
            href = a["href"].strip()
            if 'http' in href:link = href
            else:link = "http://www.qzzb.gov.cn" + href + "&leftIndex=1"
            td = tr.find_all("td", class_="cztab_bt3 cztab_bort cztab_bo")[3].text.strip()
            tmp = [title, td, link]
            data.append(tmp)
        df = pd.DataFrame(data)
        df['info'] = None
        return df

    elif "govProcurement/govMorePage.do?" in url:
        locator = (By.XPATH, "//ul[@id='DetailList']/li[1]/a")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-30:]
        try:
            locator = (By.XPATH, "//span[@id='pageIndex']")
            st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            cnum = int(st)
        except:
            cnum = 1
        if num != int(cnum):
            s1 = Select(driver.find_element_by_id('skipPage'))
            s1.select_by_value("{}".format(num))
            locator = (By.XPATH, "//ul[@id='DetailList']/li[1]/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        table = soup.find("ul", id="DetailList")
        trs = table.find_all("li")
        data = []
        for tr in trs:
            a = tr.find('a')
            try:
                title = a["title"].strip()
            except:
                title = a.text.strip()
            href = a["href"].strip()
            if 'http' in href:
                link = href
            else:
                link = "http://www.qzzb.gov.cn" + href
            td = tr.find("span").text.strip()

            tmp = [title, td, link]
            data.append(tmp)
        df = pd.DataFrame(data)
        df['info'] = None
        return df

    elif ('anQuestionList.do?' in url) or ('otherBidAnQuestion.do?' in url):
        locator = (By.XPATH, "//dl[@id='LatestListAnq']/ul/li[1]/a")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-30:]
        try:
            locator = (By.XPATH, "//span[@id='pageIndex']")
            st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            cnum = int(st)
        except:
            cnum = 1
        if num != int(cnum):
            s1 = Select(driver.find_element_by_id('skipPage'))
            s1.select_by_value("{}".format(num))
            locator = (By.XPATH, "//dl[@id='LatestListAnq']/ul/li[1]/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        table = soup.find("dl", id="LatestListAnq").ul
        trs = table.find_all("li")
        data = []
        for tr in trs:
            a = tr.find('a')
            try:
                title = a["title"].strip()
            except:
                title = a.text.strip()
            href = a["href"].strip()
            if 'http' in href:
                link = href
            else:
                link = "http://www.qzzb.gov.cn" + href
            td = tr.find("span").text.strip()
            tmp = [title, td, link]
            data.append(tmp)
        df = pd.DataFrame(data)
        df['info'] = None
        return df
    else:
        locator = (By.XPATH, "//dl[@id='LatestListWinBul']/ul/li[1]/a")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-30:]
        try:
            locator = (By.XPATH, "//span[@id='pageIndex']")
            st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            cnum = int(st)
        except:
            cnum = 1
        if num != int(cnum):
            s1 = Select(driver.find_element_by_id('skipPage'))
            s1.select_by_value("{}".format(num))
            locator = (By.XPATH, "//dl[@id='LatestListWinBul']/ul/li[1]/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        table = soup.find("dl", id="LatestListWinBul")
        trs = table.find_all("li")
        data = []
        for tr in trs:
            a = tr.find('a')
            try:
                title = a["title"].strip()
            except:
                title = a.text.strip()
            href = a["href"].strip()
            if 'http' in href:
                link = href
            else:
                link = "http://www.qzzb.gov.cn" + href
            td = tr.find("span").text.strip()
            tmp = [title, td, link]
            data.append(tmp)
        df = pd.DataFrame(data)
        df['info'] = None
        return df


def f2(driver):
    locator = (By.XPATH, "//dl[@id='LatestListPro']/table/tbody/tr[2]/td[2]/a | //ul[@id='DetailList']/li[1]/a | //dl[@id='LatestListWinBul']/ul/li[1]/a | //dl[@id='LatestListAnq']/ul/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//span[@id='totalPage']")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = int(st)
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    if "/govProcurement/govProcurementDetail.do" in url:
        locator = (By.XPATH, "//div[@class='conwz']")
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
        div = soup.find('div', class_="conwz")
        return div
    try:
        time.sleep(1)
        al = driver.switch_to_alert()
        al.accept()
        return 404
    except:
        time.sleep(1)
    if ("Internal Server Error" in str(driver.page_source)) or ('404' in str(driver.title)) or ('暂无数据' in str(driver.page_source)):
        return 404
    time.sleep(1)
    flag = 0

    locator = (By.XPATH, "//div[@class='warp'][string-length()>50]")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    if 'iframepage' in str(driver.page_source):
        locator = (By.XPATH, "//iframe[@id='iframepage']")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        driver.switch_to_frame('iframepage')
        try:
            locator = (By.XPATH, "//div[@class='page'][last()]")
            WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
        except:
            flag = 1

        if flag != 1:
            locator = (By.XPATH, '//span[@id="numPages"]')
            tnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()

            tnum = int(re.findall(r'(\d+)', tnum)[0])
            if tnum != 1:
                for _ in range(tnum - 1):
                    locator = (By.XPATH, "//button[@id='next']")
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            try:
                locator = (By.XPATH, "//div[@class='page'][{}][string-length()>10]".format(tnum))
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
            except:
                locator = (By.XPATH, "//div[@class='page'][{}][string-length()>10]".format(tnum-1))
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    time.sleep(1)
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
    time.sleep(3)
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    if flag == 1:
        div = soup.find('body')
    else:
        divs = soup.find_all('div', class_='page')
        div = ''
        for di in divs:div+=str(di)
        if (div == None) or (div == ''):div = soup.find('div', class_='warp')
    return div



data = [
    ["gcjs_zhaobiao_gg",
     "http://www.qzzb.gov.cn/project/projectList.do?centerId=-1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_zhong_liu_gg",
     "http://www.qzzb.gov.cn/project/winBulletinList.do?centerId=-1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://www.qzzb.gov.cn/project/anQuestionList.do?centerId=-1",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["zfcg_zhaobiao_gg",
     "http://www.qzzb.gov.cn/govProcurement/govMorePage.do?govProClassId=2&centerId=-1",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_biangeng_gg",
     "http://www.qzzb.gov.cn/govProcurement/govMorePage.do?govProClassId=3&centerId=-1",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhongbiao_gg",
     "http://www.qzzb.gov.cn/govProcurement/govMorePage.do?govProClassId=4&centerId=-1",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_biangeng_jieguo_gg",
     "http://www.qzzb.gov.cn/govProcurement/govMorePage.do?govProClassId=5&centerId=-1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_danyilaiyuan_gg",
     "http://www.qzzb.gov.cn/govProcurement/govMorePage.do?govProClassId=8&centerId=-1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"zbfs":"单一来源"}), f2],

    ["qsy_zhaobiao_gg",
     "http://www.qzzb.gov.cn/project/otherBidInfo.do?centerId=-1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_gqita_zhong_liu_gg",
     "http://www.qzzb.gov.cn/project/otherBidWinBulletin.do?centerId=-1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_gqita_bian_bu_gg",
     "http://www.qzzb.gov.cn/project/otherBidAnQuestion.do?centerId=-1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="福建省泉州市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","zhulong.com.cn","192.168.169.47","fujian","quanzhou"],pageloadtimeout=160)


    # driver=webdriver.Chrome()
    # url = "http://www.qzzb.gov.cn/project/otherBidAnQuestion.do?centerId=-1"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    # driver=webdriver.Chrome()
    # url = "http://www.qzzb.gov.cn/project/otherBidAnQuestion.do?centerId=-1"
    # driver.get(url)
    # for i in range(1, 6):
    #     df=f1(driver, i)
    #     print(df.values)
    #     for f in df[2].values:
    # d = f3(driver,'http://www.qzzb.gov.cn/project/projectInfo.do?projId=1099&leftIndex=1')
    # print(d)
