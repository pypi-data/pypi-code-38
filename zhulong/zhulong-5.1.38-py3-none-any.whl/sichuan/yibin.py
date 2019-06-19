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


_name_="yibin"




def f1(driver, num):
    url = driver.current_url
    if 'http://ggzy.yibin.gov.cn/Jyweb/LiuBiaoGongShiList.aspx?' in url:
        locator = (By.XPATH, "//table[@id='ctl00_Content_GridView1']/tbody/tr[2]/td[3]")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    else:
        locator = (By.XPATH, "//table[@id='ctl00_Content_GridView1']/tbody/tr[2]/td[3]/a")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-50:]
    try:
        locator = (By.XPATH, "//span[@id='lblAjax_PageIndex']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if str:
            cnum = int(str)
        else:
            page = driver.page_source
            soup = BeautifulSoup(page, 'html.parser')
            cnum = soup.find("span", id="lblAjax_PageIndex").text.strip()
    except:
        cnum = 1

    if num != int(cnum):
        locator = (By.XPATH, "//input[@id='txtAjax_PageIndex']")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).clear()

        locator = (By.XPATH, "//input[@id='txtAjax_PageIndex']")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).send_keys(num, Keys.ENTER)
        if 'http://ggzy.yibin.gov.cn/Jyweb/LiuBiaoGongShiList.aspx?' in url:
            locator = (By.XPATH, "//table[@id='ctl00_Content_GridView1']/tbody/tr[2]/td[3][not(contains(text(), '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        else:
            locator = (By.XPATH, "//table[@id='ctl00_Content_GridView1']/tbody/tr[2]/td[3]/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", id="ctl00_Content_GridView1")
    trs = table.find_all("tr")
    url = driver.current_url
    data = []
    for tr in trs[1:]:
        if 'http://ggzy.yibin.gov.cn/Jyweb/LiuBiaoGongShiList.aspx?' in url:
            try:
                a = tr.find('a')
                try:
                    title = a['title'].strip()
                except:
                    title = a.text.strip()
                link = "http://ggzy.yibin.gov.cn/Jyweb/" + a['href'].strip()
                td = tr.find_all('td')[-1].text.strip()
                datas = tr.find_all('td')[-2].text.strip()
                yy={'states': datas}
                info = json.dumps(yy, ensure_ascii=False)
            except:
                title = tr.find_all('td')[2].text.strip()
                link = '-'
                td = tr.find_all('td')[-1].text.strip()
                datas = tr.find_all('td')[-2].text.strip()
                yy = {'states': datas}
                info = json.dumps(yy, ensure_ascii=False)
        elif 'http://ggzy.yibin.gov.cn/ZFCG/Jyweb' in url:
            a = tr.find('a')
            try:
                title = a['title'].strip()
            except:
                title = a.text.strip()
            link = a['href'].strip()
            td = tr.find("td", class_="ListTableDataTimeCol").text.strip()
            info=None
        else:
            a = tr.find('a')
            try:
                title = a['title'].strip()
            except:
                title = a.text.strip()
            link = "http://ggzy.yibin.gov.cn/Jyweb/" + a['href'].strip()
            td = tr.find("td", class_="ListTableDateCol").text.strip()
            info=None
        tmp = [title, td, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.XPATH, "//table[@id='ctl00_Content_GridView1']/tbody/tr[2]/td[3]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//span[@id='lblAjax_TotalPageCount']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if str:
            num = int(str)
        else:
            page = driver.page_source
            soup = BeautifulSoup(page, 'html.parser')
            num = soup.find("span", id="lblAjax_TotalPageCount").text.strip()
    except:
        num = 1
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    time.sleep(0.5)
    html = driver.page_source
    if ("您请求的文件不存在" in html) or ("找不到文件" in html):
        return 404
    locator = (By.XPATH, "//*[@id='form1'] | //div[@class='container']")
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
    div = soup.find('div', id="cphMiddle_divJYXX")
    if div == None:
        div = soup.find('div', class_='w1200 divview')
        if div == None:
            div = soup.find('div', id="myPrintArea")
    return div



def diqu2(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, "//table[@id='ctl00_Content_GridView1']/tbody/tr[2]/td[3]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        driver.find_element_by_link_text('临港区').click()
        if f == f1:
            df = f(*krg)
            a = {"diqu": "临港区"}
            add_info(f1, a)
            return df
        else:
            return f(*krg)
    return wrap

def diqu3(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, "//table[@id='ctl00_Content_GridView1']/tbody/tr[2]/td[3]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        driver.find_element_by_link_text('翠屏区').click()
        if f == f1:
            df = f(*krg)
            a = {"diqu": "翠屏区"}
            add_info(f1, a)
            return df
        else:
            return f(*krg)
    return wrap

def diqu4(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, "//table[@id='ctl00_Content_GridView1']/tbody/tr[2]/td[3]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        driver.find_element_by_link_text('叙州区').click()
        if f == f1:
            df = f(*krg)
            a = {"diqu": "叙州区"}
            add_info(f1, a)
            return df
        else:
            return f(*krg)
    return wrap

def diqu5(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, "//table[@id='ctl00_Content_GridView1']/tbody/tr[2]/td[3]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        driver.find_element_by_link_text('南溪区').click()
        if f == f1:
            df = f(*krg)
            a = {"diqu": "南溪区"}
            add_info(f1, a)
            return df
        else:
            return f(*krg)
    return wrap

def diqu6(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, "//table[@id='ctl00_Content_GridView1']/tbody/tr[2]/td[3]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        driver.find_element_by_link_text('筠连县').click()
        if f == f1:
            df = f(*krg)
            a = {"diqu": "筠连县"}
            add_info(f1, a)
            return df
        else:
            return f(*krg)
    return wrap
#
def diqu7(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, "//table[@id='ctl00_Content_GridView1']/tbody/tr[2]/td[3]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        driver.find_element_by_link_text('屏山县').click()
        if f == f1:
            df = f(*krg)
            a = {"diqu": "屏山县"}
            add_info(f1, a)
            return df
        else:
            return f(*krg)
    return wrap

def diqu8(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, "//table[@id='ctl00_Content_GridView1']/tbody/tr[2]/td[3]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        driver.find_element_by_link_text('长宁县').click()
        if f == f1:
            df = f(*krg)
            a = {"diqu": "长宁县"}
            add_info(f1, a)
            return df
        else:
            return f(*krg)
    return wrap

def diqu9(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, "//table[@id='ctl00_Content_GridView1']/tbody/tr[2]/td[3]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        driver.find_element_by_link_text('兴文县').click()
        if f == f1:
            df = f(*krg)
            a = {"diqu": "兴文县"}
            add_info(f1, a)
            return df
        else:
            return f(*krg)
    return wrap

def diqu10(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, "//table[@id='ctl00_Content_GridView1']/tbody/tr[2]/td[3]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        driver.find_element_by_link_text('高县').click()
        if f == f1:
            df = f(*krg)
            a = {"diqu": "高县"}
            add_info(f1, a)
            return df
        else:
            return f(*krg)
    return wrap

def diqu11(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, "//table[@id='ctl00_Content_GridView1']/tbody/tr[2]/td[3]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        driver.find_element_by_link_text('珙县').click()
        if f == f1:
            df = f(*krg)
            a = {"diqu": "珙县"}
            add_info(f1, a)
            return df
        else:
            return f(*krg)
    return wrap

def diqu12(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, "//table[@id='ctl00_Content_GridView1']/tbody/tr[2]/td[3]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        driver.find_element_by_link_text('江安县').click()
        if f == f1:
            df = f(*krg)
            a = {"diqu": "江安县"}
            add_info(f1, a)
            return df
        else:
            return f(*krg)
    return wrap




data = [
    ["gcjs_gqita_yuzhaobiao_gg",
     "http://ggzy.yibin.gov.cn/Jyweb/JYXTXiangMuXinXiList.aspx?type=%E5%BB%BA%E8%AE%BE%E5%B7%A5%E7%A8%8B&subType=130",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gglx':'项目信息'}),f2],

    ["gcjs_zhaobiao_gg",
     "http://ggzy.yibin.gov.cn/Jyweb/ZhaoBaoGongGaoList.aspx?Type=%E5%BB%BA%E8%AE%BE%E5%B7%A5%E7%A8%8B&SubType=260",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_biangeng_gg",
     "http://ggzy.yibin.gov.cn/Jyweb/BianGengGongGaoList.aspx?Type=%E5%BB%BA%E8%AE%BE%E5%B7%A5%E7%A8%8B&SubType=110",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_liubiao_zhongzhi_gg",
     "http://ggzy.yibin.gov.cn/Jyweb/ZhongZhiGongGaoList.aspx?Type=%E5%BB%BA%E8%AE%BE%E5%B7%A5%E7%A8%8B&SubType=111",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zgysjg_gg",
     "http://ggzy.yibin.gov.cn/Jyweb/KaiBiaoJiLuList.aspx?Type=%E5%BB%BA%E8%AE%BE%E5%B7%A5%E7%A8%8B&SubType=112",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiaohx_gg",
     "http://ggzy.yibin.gov.cn/Jyweb/ZhongBiaoHouXuanRenList.aspx?Type=%E5%BB%BA%E8%AE%BE%E5%B7%A5%E7%A8%8B&SubType=120",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_zhonghxbiangeng_gg",
     "http://ggzy.yibin.gov.cn/Jyweb/ZhongBiaoHouXuanRenBGList.aspx?Type=%E5%BB%BA%E8%AE%BE%E5%B7%A5%E7%A8%8B&SubType=125",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gglx':'评标结果变更公示'}), f2],

    ["gcjs_zhongbiao_gg",
     "http://ggzy.yibin.gov.cn/Jyweb/ZhongBiaoJieGuoGongShiList.aspx?Type=%E5%BB%BA%E8%AE%BE%E5%B7%A5%E7%A8%8B&SubType=121",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_zhongbiangeng_gg",
     "http://ggzy.yibin.gov.cn/Jyweb/ZhongBiaoJieGuoGongShiBGList.aspx?Type=%E5%BB%BA%E8%AE%BE%E5%B7%A5%E7%A8%8B&SubType=135",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gglx':'中标结果变更公示'}), f2],

    ["gcjs_liubiao_gg",
     "http://ggzy.yibin.gov.cn/Jyweb/LiuBiaoGongShiList.aspx?Type=%E5%BB%BA%E8%AE%BE%E5%B7%A5%E7%A8%8B&SubType=251",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_hetong_gg",
     "http://ggzy.yibin.gov.cn/Jyweb/HeTongGongShiList.aspx?Type=%E5%BB%BA%E8%AE%BE%E5%B7%A5%E7%A8%8B&SubType=252",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_diqu1_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=320",
    ["name", "ggstart_time", "href", "info"],add_info(f1,{'diqu':'宜宾市'}),f2],

    ["zfcg_biangeng_diqu1_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=410",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'diqu':'宜宾市'}), f2],

    ["zfcg_gqita_zhong_liu_diqu1_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=600",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu':'宜宾市'}), f2],

    ["zfcg_gqita_jieguobiangeng_diqu1_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=630",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'diqu':'宜宾市','gglx':'结果变更公告'}), f2],
    #
    ["zfcg_zhaobiao_diqu2_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=320",
     ["name", "ggstart_time", "href", "info"], diqu2(f1), diqu2(f2)],

    ["zfcg_biangeng_diqu2_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=410",
     ["name", "ggstart_time", "href", "info"], diqu2(f1), diqu2(f2)],

    ["zfcg_gqita_zhong_liu_diqu2_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=600",
     ["name", "ggstart_time", "href", "info"], diqu2(f1), diqu2(f2)],

    ["zfcg_gqita_jieguobiangeng_diqu2_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=630",
     ["name", "ggstart_time", "href", "info"], diqu2(add_info(f1,{'gglx':'结果变更公告'})), diqu2(f2)],
    #
    ["zfcg_zhaobiao_diqu3_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=320",
     ["name", "ggstart_time", "href", "info"], diqu3(f1), diqu3(f2)],

    ["zfcg_biangeng_diqu3_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=410",
     ["name", "ggstart_time", "href", "info"], diqu3(f1), diqu3(f2)],

    ["zfcg_gqita_zhong_liu_diqu3_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=600",
     ["name", "ggstart_time", "href", "info"], diqu3(f1), diqu3(f2)],
    #
    ["zfcg_zhaobiao_diqu4_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=320",
     ["name", "ggstart_time", "href", "info"], diqu4(f1), diqu4(f2)],

    ["zfcg_biangeng_diqu4_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=410",
     ["name", "ggstart_time", "href", "info"], diqu4(f1), diqu4(f2)],

    ["zfcg_gqita_zhong_liu_diqu4_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=600",
     ["name", "ggstart_time", "href", "info"], diqu4(f1), diqu4(f2)],
    #
    ["zfcg_zhaobiao_diqu5_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=320",
     ["name", "ggstart_time", "href", "info"], diqu5(f1), diqu5(f2)],

    ["zfcg_biangeng_diqu5_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=410",
     ["name", "ggstart_time", "href", "info"], diqu5(f1), diqu5(f2)],

    ["zfcg_gqita_zhong_liu_diqu5_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=600",
     ["name", "ggstart_time", "href", "info"], diqu5(f1), diqu5(f2)],

    #

    ["zfcg_zhaobiao_diqu6_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=320",
     ["name", "ggstart_time", "href", "info"], diqu6(f1), diqu6(f2)],

    ["zfcg_biangeng_diqu6_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=410",
     ["name", "ggstart_time", "href", "info"], diqu6(f1), diqu6(f2)],

    ["zfcg_gqita_zhong_liu_diqu6_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=600",
     ["name", "ggstart_time", "href", "info"], diqu6(f1), diqu6(f2)],

    ["zfcg_gqita_jieguobiangeng_diqu6_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=630",
     ["name", "ggstart_time", "href", "info"], diqu6(add_info(f1,{'gglx':'结果变更公告'})), diqu6(f2)],
    #
    ["zfcg_zhaobiao_diqu7_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=320",
     ["name", "ggstart_time", "href", "info"], diqu7(f1), diqu7(f2)],

    ["zfcg_biangeng_diqu7_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=410",
     ["name", "ggstart_time", "href", "info"], diqu7(f1), diqu7(f2)],

    ["zfcg_gqita_zhong_liu_diqu7_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=600",
     ["name", "ggstart_time", "href", "info"], diqu7(f1), diqu7(f2)],

    #
    ["zfcg_zhaobiao_diqu8_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=320",
     ["name", "ggstart_time", "href", "info"], diqu8(f1), diqu8(f2)],

    ["zfcg_biangeng_diqu8_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=410",
     ["name", "ggstart_time", "href", "info"], diqu8(f1), diqu8(f2)],

    ["zfcg_gqita_zhong_liu_diqu8_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=600",
     ["name", "ggstart_time", "href", "info"], diqu8(f1), diqu8(f2)],
    #
    ["zfcg_zhaobiao_diqu9_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=320",
     ["name", "ggstart_time", "href", "info"], diqu9(f1), diqu9(f2)],

    ["zfcg_biangeng_diqu9_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=410",
     ["name", "ggstart_time", "href", "info"], diqu9(f1), diqu9(f2)],

    ["zfcg_gqita_zhong_liu_diqu9_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=600",
     ["name", "ggstart_time", "href", "info"], diqu9(f1), diqu9(f2)],

    ["zfcg_gqita_jieguobiangeng_diqu9_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=630",
     ["name", "ggstart_time", "href", "info"], diqu9(add_info(f1,{'gglx':'结果变更公告'})), diqu9(f2)],
    #
    ["zfcg_zhaobiao_diqu10_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=320",
     ["name", "ggstart_time", "href", "info"], diqu10(f1), diqu10(f2)],

    ["zfcg_biangeng_diqu10_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=410",
     ["name", "ggstart_time", "href", "info"], diqu10(f1), diqu10(f2)],

    ["zfcg_gqita_zhong_liu_diqu10_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=600",
     ["name", "ggstart_time", "href", "info"], diqu10(f1), diqu10(f2)],
    #
    ["zfcg_zhaobiao_diqu11_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=320",
     ["name", "ggstart_time", "href", "info"], diqu11(f1), diqu11(f2)],

    ["zfcg_biangeng_diqu11_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=410",
     ["name", "ggstart_time", "href", "info"], diqu11(f1), diqu11(f2)],

    ["zfcg_gqita_zhong_liu_diqu11_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=600",
     ["name", "ggstart_time", "href", "info"], diqu11(f1), diqu11(f2)],
    #
    ["zfcg_zhaobiao_diqu12_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=320",
     ["name", "ggstart_time", "href", "info"], diqu12(f1), diqu12(f2)],

    ["zfcg_biangeng_diqu12_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=410",
     ["name", "ggstart_time", "href", "info"], diqu12(f1), diqu12(f2)],

    ["zfcg_gqita_zhong_liu_diqu12_gg",
     "http://ggzy.yibin.gov.cn/ZFCG/Jyweb/JYGGXXList.aspx?Type=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&SubType=600",
     ["name", "ggstart_time", "href", "info"], diqu12(f1), diqu12(f2)],
    #
    #
    ["qsy_zhaobiao_gg",
     "http://ggzy.yibin.gov.cn/Jyweb/JYXXList.aspx?type=%E5%9B%BD%E4%BC%81%E6%8B%9B%E6%A0%87&subType=601",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'国企招标'}), f2],

    ["qsy_biangeng_gg",
     "http://ggzy.yibin.gov.cn/Jyweb/JYXXList.aspx?Type=%E5%9B%BD%E4%BC%81%E6%8B%9B%E6%A0%87&SubType=602",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'国企招标'}), f2],

    ["qsy_zhongbiao_gg",
     "http://ggzy.yibin.gov.cn/Jyweb/JYXXList.aspx?Type=%E5%9B%BD%E4%BC%81%E6%8B%9B%E6%A0%87&SubType=603",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'国企招标'}), f2],
    #
    ["jqita_zhaobiao_gg",
     "http://ggzy.yibin.gov.cn/Jyweb/JYXXList.aspx?type=%E5%85%B6%E4%BB%96%E9%A1%B9%E7%9B%AE&subType=100",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'其他项目'}), f2],

    ["jqita_biangeng_gg",
     "http://ggzy.yibin.gov.cn/Jyweb/JYXXList.aspx?Type=%E5%85%B6%E4%BB%96%E9%A1%B9%E7%9B%AE&SubType=110",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'其他项目'}), f2],

    ["jqita_gqita_zhong_liu_gg",
     "http://ggzy.yibin.gov.cn/Jyweb/JYXXList.aspx?Type=%E5%85%B6%E4%BB%96%E9%A1%B9%E7%9B%AE&SubType=120",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'其他项目'}), f2],

    ["jqita_gqita_yuzhaobiao_gg",
     "http://ggzy.yibin.gov.cn/Jyweb/JYXXList.aspx?Type=%E5%85%B6%E4%BB%96%E9%A1%B9%E7%9B%AE&SubType=130",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'其他项目','gglx':'项目信息'}), f2],

]



def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省宜宾市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","sichuan","yibin"])

