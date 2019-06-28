import json
import time
import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lmfscrap import web

_name_="heze"

from zhulong.util.etl import est_meta, est_html, add_info

n = None
starte_url = None

def f1(driver, num):
    if n == 1:
        df = f1_data_1(driver, num, n)
        return df
    else:
        df = f1_data(driver, num, n)
        return df

def f1_data(driver, num, n):
    url = driver.current_url
    locator = (By.XPATH, "//li[contains(@id, 'tabL{}')]".format(n))
    li_name = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    locator = (By.XPATH, "//li[@class='current']")
    li_class_name = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    if li_name != li_class_name:
        locator = (By.XPATH, "//li[contains(@id, 'tabL{}')]".format(n))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        time.sleep(0.8)
    try:
        locator = (By.XPATH, '//*[@id="ContentPlaceHolder1_lblCurrent{}"]'.format(n))
        cnum = WebDriverWait(driver, 15).until(EC.presence_of_element_located(locator)).text
    except:
        time.sleep(1)
        locator = (By.XPATH, '//*[@id="ContentPlaceHolder1_lblCurrent{}"]'.format(n))
        cnum = WebDriverWait(driver, 15).until(EC.presence_of_element_located(locator)).text

    val = driver.find_element_by_xpath('//*[@id="contentL{}"]/div/ul/li[1]/a'.format(n)).get_attribute('href')[-15:]
    if num != int(cnum):
        for _ in range(abs(num-int(cnum))):
            url_1 = driver.current_url
            if url_1 != url:
                driver.back()
            if num > int(cnum):
                driver.execute_script("javascript:__doPostBack('ctl00$ContentPlaceHolder1$lbtnDown{}','')".format(n))
            else:
                driver.execute_script("javascript:__doPostBack('ctl00$ContentPlaceHolder1$lbntUp{}','')".format(n))
            url_1 = driver.current_url
            if url_1 != url:
                driver.back()
            locator = (By.XPATH, "//li[contains(@id, 'tabL{}')]".format(n))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            url_1 = driver.current_url
            if url_1 != url:
                driver.back()
            time.sleep(0.5)
            locator = (By.XPATH, '//*[@id="contentL{0}"]/div/ul/li[1]/a[not(contains(@href, "{1}"))]'.format(n, val))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            locator = (By.XPATH, '//*[@id="ContentPlaceHolder1_lblCurrent{}"]'.format(n))
            cn = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
            if int(cn) == num:
                break
    locator = (By.XPATH, '//*[@id="ContentPlaceHolder1_lblCurrent{}"]'.format(n))
    cn = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    if int(cn) != num:
        raise TimeoutError
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    tbody = soup.find("div", id="contentL{}".format(n))
    trs = tbody.find_all("li")
    data = []
    for tr in trs:
        info = {}
        a = tr.find("a")
        title = tr.find("h2")
        stat = tr.find('div', class_='info_right')
        try:
            date = stat.find_all("em")[-1].extract().text.strip()
        except:
            date = '-'
        if stat.find("em"):
            diqu = stat.find("em").text.strip()
            if diqu: info['diqu'] = diqu
        stat2 = tr.find('div', class_='info_left')
        if stat2.find_all('em')[0]:
            jylx = stat2.find_all('em')[0].text.strip()
            if jylx: info['jylx'] = jylx
        if stat2.find_all('em')[1]:
            zbfs = stat2.find_all('em')[1].text.strip()
            if zbfs: info['zbfs'] = zbfs
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:
            info = None

        tmp = [title.text.strip(), date, "http://hzsggzyjy.gov.cn/" + a["href"], info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f1_data_1(driver, num, n):
    url = driver.current_url
    locator = (By.XPATH, "//li[contains(@id, 'tabL{}')]".format(n))
    li_name = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    locator = (By.XPATH, "//li[@class='current']")
    li_class_name = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    if li_name != li_class_name:
        locator = (By.XPATH, "//li[contains(@id, 'tabL{}')]".format(n))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        time.sleep(0.8)
    try:
        locator = (By.XPATH, '//*[@id="ContentPlaceHolder1_lblCurrent"]')
        cnum = WebDriverWait(driver, 15).until(EC.presence_of_element_located(locator)).text
    except:
        time.sleep(1)
        locator = (By.XPATH, '//*[@id="ContentPlaceHolder1_lblCurrent"]')
        cnum = WebDriverWait(driver, 15).until(EC.presence_of_element_located(locator)).text

    val = driver.find_element_by_xpath('//*[@id="contentL{}"]/div/ul/li[1]/a'.format(n)).get_attribute('href')[-15:]
    if num != int(cnum):
        for _ in range(abs(num - int(cnum))):
            url_1 = driver.current_url
            if url_1 != url:
                driver.back()
            if num > int(cnum):
                driver.execute_script("javascript:__doPostBack('ctl00$ContentPlaceHolder1$lbtnDown','')")
            else:
                driver.execute_script("javascript:__doPostBack('ctl00$ContentPlaceHolder1$lbntUp','')")
            url_1 = driver.current_url
            if url_1 != url:
                driver.back()

            time.sleep(0.5)
            locator = (By.XPATH, '//*[@id="contentL{0}"]/div/ul/li[1]/a[not(contains(@href, "{1}"))]'.format(n, val))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            locator = (By.XPATH, '//*[@id="ContentPlaceHolder1_lblCurrent"]')
            cn = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
            if int(cn) == num:
                break
    locator = (By.XPATH, '//*[@id="ContentPlaceHolder1_lblCurrent"]')
    cn = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    if int(cn) != num:
        raise TimeoutError
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    tbody = soup.find("div", id="contentL{}".format(n))
    trs = tbody.find_all("li")
    data = []
    for tr in trs:
        info = {}
        a = tr.find("a")
        title = tr.find("h2")
        stat = tr.find('div', class_='info_right')
        try:
            date = stat.find_all("em")[-1].extract().text.strip()
        except:
            date = '-'
        if stat.find("em"):
            diqu = stat.find("em").text.strip()
            if diqu:info['diqu'] = diqu
        stat2 = tr.find('div', class_='info_left')
        if stat2.find_all('em')[0]:
            jylx = stat2.find_all('em')[0].text.strip()
            if jylx:info['jylx'] = jylx
        if stat2.find_all('em')[1]:
            zbfs = stat2.find_all('em')[1].text.strip()
            if zbfs:info['zbfs'] = zbfs
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:info = None

        tmp = [title.text.strip(), date, "http://hzsggzyjy.gov.cn/" + a["href"], info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    global n,starte_url
    n = None
    starte_url = None
    url = driver.current_url
    n = int(url.rsplit('&', maxsplit=1)[1])
    starte_url = url.rsplit('&', maxsplit=1)[0]
    driver.get(starte_url)
    if n == 1:
        num = f2_data_1(driver, n)
        driver.quit()
        return num
    else:
        num = f2_data(driver, n)
        driver.quit()
        return num


def f2_data(driver, n):
    locator = (By.XPATH, "//li[contains(@id, 'tabL{}')]".format(n))
    li_name = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    locator = (By.XPATH, "//li[@class='current']")
    li_class_name = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    if li_name != li_class_name:
        locator = (By.XPATH, "//li[contains(@id, 'tabL{}')]".format(n))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        time.sleep(2)
    locator = (By.XPATH, "//span[@id='ContentPlaceHolder1_lblTotal{}']".format(n))
    page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text

    return int(page)


def f2_data_1(driver, n):
    locator = (By.XPATH, "//li[contains(@id, 'tabL{}')]".format(n))
    li_name = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    locator = (By.XPATH, "//li[@class='current']")
    li_class_name = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    if li_name != li_class_name:
        locator = (By.XPATH, "//li[contains(@id, 'tabL{}')]".format(n))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        time.sleep(2)
    locator = (By.XPATH, "//span[@id='ContentPlaceHolder1_lblTotal']")
    page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text

    return int(page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='ContentPlaceHolder1_contents'][string-length()>10] | //div[@class='NewsPage'][string-length()>30]")
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
    div = soup.find('div', id="ContentPlaceHolder1_contents")
    if div == None:
        div = soup.find('div', class_='NewsPage')
    return div


data = [
    ["gcjs_yucai_gg","http://hzsggzyjy.gov.cn/cityInfoList.aspx?s=1&t=1&8",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["jqita_yucai_huowu_gg", "http://hzsggzyjy.gov.cn/cityInfoList.aspx?s=1&t=5&8",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'货物'}),f2],

    ["jqita_yucai_fuwu_gg", "http://hzsggzyjy.gov.cn/cityInfoList.aspx?s=1&t=6&8",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'服务'}),f2],
    #
    ["gcjs_gqita_zhao_bian_gg", "http://hzsggzyjy.gov.cn/cityInfoList.aspx?s=1&t=1&1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_gqita_zhao_bian_huowu_gg", "http://hzsggzyjy.gov.cn/cityInfoList.aspx?s=1&t=5&1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'货物'}), f2],

    ["jqita_gqita_zhao_bian_fuwu_gg", "http://hzsggzyjy.gov.cn/cityInfoList.aspx?s=1&t=6&1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'服务'}), f2],
    #
    ["gcjs_gqita_zhong_liu_gg", "http://hzsggzyjy.gov.cn/cityInfoList.aspx?s=1&t=1&4",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_gqita_zhong_liu_huowu_gg", "http://hzsggzyjy.gov.cn/cityInfoList.aspx?s=1&t=5&4",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'货物'}), f2],

    ["jqita_gqita_zhong_liu_fuwu_gg", "http://hzsggzyjy.gov.cn/cityInfoList.aspx?s=1&t=6&4",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'服务'}), f2],
    #
    ["gcjs_yanshou_gg", "http://hzsggzyjy.gov.cn/cityInfoList.aspx?s=1&t=1&7",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_yanshou_huowu_gg", "http://hzsggzyjy.gov.cn/cityInfoList.aspx?s=1&t=5&7",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'货物'}), f2],

    ["jqita_yanshou_fuwu_gg", "http://hzsggzyjy.gov.cn/cityInfoList.aspx?s=1&t=6&7",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'服务'}), f2],
    #
    ["gcjs_zhaobiao_danyilaiyuan_gg", "http://hzsggzyjy.gov.cn/cityInfoList.aspx?s=1&t=1&5",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhaobiao_danyilaiyuan_huowu_gg", "http://hzsggzyjy.gov.cn/cityInfoList.aspx?s=1&t=5&5",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'货物','zbfs':'单一来源'}), f2],

    ["jqita_zhaobiao_danyilaiyuan_fuwu_gg", "http://hzsggzyjy.gov.cn/cityInfoList.aspx?s=1&t=6&5",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'服务','zbfs':'单一来源'}), f2],

]



def work(conp,**args):
    est_meta(conp,data=data,diqu="山东省菏泽市",**args)
    est_html(conp,f=f3,**args)

# 修改日期：2019/6/28
# 设置线程数为1，等待时长为120是最快的
if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shandong","heze"],pageloadtimeout=120,pageLoadStrategy="none",num=1,headless=False)


