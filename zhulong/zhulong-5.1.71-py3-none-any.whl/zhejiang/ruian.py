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


_name_="ruian"



def f1(driver, num):
    locator = (By.XPATH, "//*[@id='MoreInfoList1_DataGrid1']/tbody/tr[1]/td[2]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//td[@valign='bottom']/font[3]")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = int(st)
    if num != int(cnum):
        val = driver.find_element_by_xpath("//*[@id='MoreInfoList1_DataGrid1']/tbody/tr[1]/td[2]/a").get_attribute('href')[-40:]
        driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','{}')".format(num))
        try:
            locator = (By.XPATH, "//*[@id='MoreInfoList1_DataGrid1']/tbody/tr[1]/td[2]/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            driver.refresh()
            locator = (By.XPATH, "//*[@id='MoreInfoList1_DataGrid1']/tbody/tr[1]/td[2]/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", id="MoreInfoList1_DataGrid1")
    trs = table.find_all("tr")
    data = []
    for tr in trs:
        a = tr.find("a")
        try:
            title = a["title"].strip()
        except:
            title = a.text.strip()
        td = tr.find_all("td")[2].text.strip()
        link = "http://www.raztb.com"+a["href"].strip()
        tmp = [title, td, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df




def f2(driver):
    locator = (By.XPATH, "//*[@id='MoreInfoList1_DataGrid1']/tbody/tr[1]/td[2]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//td[@valign='bottom']/font[2]")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = int(st)
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    if '抱歉，系统发生了错误！' in driver.page_source:
        return 404
    locator = (By.XPATH, "//table[@id='tblInfo']")
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
    div = soup.find('table', id="tblInfo")
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.raztb.com/TPFront/jyxx/002001/002001001/MoreInfo.aspx?CategoryNum=002001001",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.raztb.com/TPFront/jyxx/002001/002001002/MoreInfo.aspx?CategoryNum=002001002",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://www.raztb.com/TPFront/jyxx/002001/002001003/MoreInfo.aspx?CategoryNum=002001003",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_biangeng_gg",
     "http://www.raztb.com/TPFront/jyxx/002001/002001004/MoreInfo.aspx?CategoryNum=002001004",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_kaibiao_gg",
     "http://www.raztb.com/TPFront/jyxx/002001/002001005/MoreInfo.aspx?CategoryNum=002001005",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://www.raztb.com/TPFront/jyxx/002002/002002001/MoreInfo.aspx?CategoryNum=002002001",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://www.raztb.com/TPFront/jyxx/002002/002002007/MoreInfo.aspx?CategoryNum=002002007",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_zhonghx_liu_gg",
     "http://www.raztb.com/TPFront/jyxx/002002/002002002/MoreInfo.aspx?CategoryNum=002002002",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://www.raztb.com/TPFront/jyxx/002002/002002004/MoreInfo.aspx?CategoryNum=002002004",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_yucai_gg",
     "http://www.raztb.com/TPFront/jyxx/002002/002002003/MoreInfo.aspx?CategoryNum=002002003",
     ["name", "ggstart_time", "href", "info"],f1,f2],


    ["jqita_zhaobiao_gg",
     "http://www.raztb.com/TPFront/jyxx/002007/002007001/MoreInfo.aspx?CategoryNum=002007001",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'社会交易项目'}), f2],

    ["jqita_zhongbiaohx_gg",
     "http://www.raztb.com/TPFront/jyxx/002007/002007002/MoreInfo.aspx?CategoryNum=002007002",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'社会交易项目'}), f2],

    ["jqita_zhongbiao_gg",
     "http://www.raztb.com/TPFront/jyxx/002007/002007003/MoreInfo.aspx?CategoryNum=002007003",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'社会交易项目'}), f2],

    ["jqita_biangeng_gg",
     "http://www.raztb.com/TPFront/jyxx/002007/002007004/MoreInfo.aspx?CategoryNum=002007004",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'社会交易项目'}), f2],


    ["qsy_zhaobiao_gg",
     "http://www.raztb.com/TPFront/jyxx/002008/002008001/MoreInfo.aspx?CategoryNum=002008001",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'国企采购交易'}), f2],

    ["qsy_biangeng_gg",
     "http://www.raztb.com/TPFront/jyxx/002008/002008002/MoreInfo.aspx?CategoryNum=002008002",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'国企采购交易'}), f2],

    ["qsy_zhongbiaohx_gg",
     "http://www.raztb.com/TPFront/jyxx/002008/002008003/MoreInfo.aspx?CategoryNum=002008003",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'国企采购交易'}), f2],

    ["qsy_zhongbiao_gg",
     "http://www.raztb.com/TPFront/jyxx/002008/002008004/MoreInfo.aspx?CategoryNum=002008004",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'国企采购交易'}), f2],

    ["qsy_yucai_gg",
     "http://www.raztb.com/TPFront/jyxx/002008/002008005/MoreInfo.aspx?CategoryNum=002008005",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'国企采购交易'}), f2],
]


def work(conp,**args):
    est_meta(conp,data=data,diqu="浙江省瑞安市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","zhejiang","ruian"])

