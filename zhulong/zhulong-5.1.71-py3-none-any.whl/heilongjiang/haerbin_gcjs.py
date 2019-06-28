import time

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json

from zhulong.util.etl import est_tbs, est_meta, est_html, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url="http://www.hljcg.gov.cn/xwzs!queryXwxxqx.action?lbbh=52301"
# driver=webdriver.Chrome()
# driver.maximize_window()
# driver.get(url)
# # #


_name_='haerbin'

def f1(driver, num):
    locator = (By.XPATH, '//*[@id="GV_Data"]/tbody/tr[1]/td[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    while True:
        try:
            cnum = driver.find_element_by_xpath('//*[@id="GV_Data"]/tbody/tr[last()]/td/table/tbody/tr/td/span').text.strip()
        except:
            cnum=1
        cnum=int(cnum)
        if cnum == num:
            break
        if cnum <= num:
            if (num//10-cnum//10)>=2 or ((num//10-cnum//10)==1 and num%10!=0 ):
                val = driver.find_element_by_xpath('//*[@id="GV_Data"]/tbody/tr[1]/td[2]/a').text
                driver.find_element_by_xpath('//*[@id="GV_Data"]/tbody/tr[last()]/td/table/tbody/tr/td[last()]').click()
                locator = (By.XPATH, '//*[@id="GV_Data"]/tbody/tr[1]/td[2]/a[not(contains(string(),"%s"))]' % val)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            else:
                val = driver.find_element_by_xpath('//*[@id="GV_Data"]/tbody/tr[1]/td[2]/a').text
                driver.execute_script("javascript:__doPostBack('GV_Data','Page${}')".format(num))
                locator = (By.XPATH, '//*[@id="GV_Data"]/tbody/tr[1]/td[2]/a[not(contains(string(),"%s"))]' % val)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        if cnum >= num:
            if (cnum//10-num//10)>=2 or ((cnum//10-num//10)==1 and cnum%10!=0 ):
                val = driver.find_element_by_xpath('//*[@id="GV_Data"]/tbody/tr[1]/td[2]/a').text
                driver.find_element_by_xpath('//*[@id="GV_Data"]/tbody/tr[last()]/td/table/tbody/tr/td[1]/a').click()
                locator = (By.XPATH, '//*[@id="GV_Data"]/tbody/tr[1]/td[2]/a[not(contains(string(),"%s"))]' % val)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            else:
                val = driver.find_element_by_xpath('//*[@id="GV_Data"]/tbody/tr[1]/td[2]/a').text
                driver.execute_script("javascript:__doPostBack('GV_Data','Page${}')".format(num))
                locator = (By.XPATH, '//*[@id="GV_Data"]/tbody/tr[1]/td[2]/a[not(contains(string(),"%s"))]' % val)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', id='GV_Data')
    divs = div.find_all('tr', style="height:22px;")
    c_title=driver.title
    for li in divs:
        tds = li.find_all('td')
        href_ = tds[1].a['href']
        name = tds[1].a.get_text()
        ggstart_time = tds[2].get_text()
        gclx=re.findall('^\[(.*?)\]',name)
        driver.execute_script(href_)
        WebDriverWait(driver, 10).until( lambda driver:driver.title != c_title)
        href = driver.current_url
        driver.back()
        if gclx:
            info={"gclx":gclx}
            info=json.dumps(info,ensure_ascii=False)
        else:
            info=None
        tmp = [name, ggstart_time, href,info]

        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df



def f2(driver):
    locator = (By.XPATH, '//*[@id="GV_Data"]/tbody/tr[1]/td[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        driver.find_element_by_xpath('//*[@id="GV_Data"]/tbody/tr[last()]/td/table/tbody/tr/td[last()]').text
    except:
        total=1
        driver.quit()
        return total

    while True:
        val = driver.find_element_by_xpath('//*[@id="GV_Data"]/tbody/tr[1]/td[2]/a').text

        driver.find_element_by_xpath('//*[@id="GV_Data"]/tbody/tr[last()]/td/table/tbody/tr/td[last()]').click()
        locator = (By.XPATH, '//*[@id="GV_Data"]/tbody/tr[1]/td[2]/a[not(contains(string(),"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        try:
            driver.find_element_by_xpath('//*[@id="GV_Data"]/tbody/tr[last()]/td/table/tbody/tr/td[last()]/a')
        except:
            total = driver.find_element_by_xpath('//*[@id="GV_Data"]/tbody/tr[last()]/td/table/tbody/tr/td[last()]').text
            break

    total = int(total)
    driver.quit()

    return total



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@id="main_box"]/table/tbody/tr[4]')

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
    div = soup.find('div', id="main_box").find('table').find('tbody').find_all('tr', recursive=False)[3]

    return div


data = [
    ["gcjs_zhaobiao_tujian_gg", "http://113.6.234.4/Bid_Front/ZBMore.aspx?t=%E5%9C%9F%E5%BB%BA",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"土建"}), f2],
    ["gcjs_zhaobiao_shizheng_gg", "http://113.6.234.4/Bid_Front/ZBMore.aspx?t=%E5%B8%82%E6%94%BF",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"市政"}), f2],
    ["gcjs_zhaobiao_jianli_gg", "http://113.6.234.4/Bid_Front/ZBMore.aspx?t=%E7%9B%91%E7%90%86",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"监理"}), f2],
    ["gcjs_zhaobiao_tielu_gg", "http://113.6.234.4/Bid_Front/ZBMore.aspx?t=%E9%93%81%E8%B7%AF",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"铁路"}), f2],
    ["gcjs_zhaobiao_huowu_gg", "http://113.6.234.4/Bid_Front/ZBMore.aspx?t=%E8%B4%A7%E7%89%A9",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"货物"}), f2],
    ["gcjs_zhaobiao_kancha_gg", "http://113.6.234.4/Bid_Front/ZBMore.aspx?t=%E5%8B%98%E5%AF%9F%E8%AE%BE%E8%AE%A1",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"勘察设计"}), f2],
    ["gcjs_zhaobiao_qttujian_gg", "http://113.6.234.4/Bid_Front/ZBMore.aspx?t=%E5%85%B6%E5%AE%83(%E5%9C%9F%E5%BB%BA)",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"其他(土建)"}), f2],
    ["gcjs_zhaobiao_qthuowu_gg", "http://113.6.234.4/Bid_Front/ZBMore.aspx?t=%E5%85%B6%E5%AE%83(%E8%B4%A7%E7%89%A9)",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"其他(货物)"}), f2],
    ["gcjs_zhaobiao_qtkancha_gg", "http://113.6.234.4/Bid_Front/ZBMore.aspx?t=%E5%85%B6%E5%AE%83(%E5%8B%98%E5%AF%9F%E8%AE%BE%E8%AE%A1)",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"其他(勘察设计)"}), f2],
    ["gcjs_zhaobiao_qita_gg", "http://113.6.234.4/Bid_Front/ZBMore.aspx?t=%E5%85%B6%E5%AE%83",["name", "ggstart_time", "href", "info"], add_info(f1,{"gclx":"其他"}), f2],
    ["gcjs_zhongbiaohx_gg", "http://113.6.234.4/Bid_Front/KBMore.aspx?t=%E5%85%A8%E9%83%A8",["name","ggstart_time","href","info"], f1, f2],
    ["gcjs_gqita_baoming_gg", "http://113.6.234.4/Bid_Front/More.aspx?t=3",["name","ggstart_time","href","info"], add_info(f1,{"tag":"投标报名信息"}), f2],
    ["gcjs_gqita_kb_gg", "http://113.6.234.4/Bid_Front/More.aspx?t=2",["name","ggstart_time","href","info"], add_info(f1,{"tag":"开标信息"}), f2],
    ["gcjs_gqita_tongzhi_gg", "http://113.6.234.4/Bid_Front/More.aspx?t=5",["name","ggstart_time","href","info"], add_info(f1,{"tag":"重要通知"}), f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="黑龙江省哈尔滨市",**args)
    est_html(conp,f=f3,**args)

if __name__=='__main__':

    work(conp=["postgres", "since2015", "192.168.3.171", "heilongjiang", "haerbin"],headless=False,num=1)
    pass