
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


# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]


# url="https://ggzy.changsha.gov.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type2"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

from zhulong.util.etl import add_info,est_meta,est_html,est_tbs


_name_="longquan"


def f1_data(driver, cnum, stitle):
    """
    保证地区只选龙泉市的
    :param driver:
    :param cnum:
    :param stitle:
    :return:
    """
    locator = (By.XPATH, "(//td[@class='LeftMenuJsgc'])[{}]".format(cnum))
    jtitle = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    if stitle != jtitle:
        driver.find_element_by_xpath("(//td[@class='LeftMenuJsgc'])[{}]".format(cnum)).click()
        locator = (By.XPATH, "(//font[@class='currentpostionfont'])[last()][contains(text(),'%s')]" % jtitle)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))


def f1(driver, num):

    url = driver.current_url
    try:
        locator = (By.XPATH, "(//font[@class='currentpostionfont'])[last()]")
        stitle = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        f1_data(driver, 3, stitle)
        locator = (By.XPATH, "(//tr[@height='25']/td/a)[1]")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    except:
        html_data = driver.page_source
        if "本栏目暂时没有内容" in html_data:
            return
    try:
        locator = (By.XPATH, "//td[@class='huifont']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        cnum = re.findall(r'(\d+)/', str)[0]
    except:
        cnum = 1
    # print(cnum)
    url = driver.current_url

    if num != int(cnum):

        if "Paging" not in url:
            s = "?Paging=%d" % (num) if num > 1 else "?Paging=1"
            url = url + s
        elif num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
            # print(cnum)
        driver.get(url)
        try:
            locator = (By.XPATH, "(//tr[@height='25']/td/a)[1][string()!='%s']" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            driver.refresh()
            locator = (By.XPATH, "(//tr[@height='25']/td/a)[1][string()!='%s']" % val)
            WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator))



    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    table = soup.find("table", cellspacing='3')

    trs = table.find_all("tr", height="25")
    data = []
    for tr in trs:
        a = tr.find("a")
        try:
            title = a["title"].strip()
        except:
            title = a.text.strip()
        try:
            link = a["href"]
        except:
            continue
        td = tr.find("font", color="#000000").text.strip()

        link = "http://www.lssggzy.com" + link.strip()

        tmp = [title, td, link]
        data.append(tmp)


    df = pd.DataFrame(data)
    df['info'] = None
    return df



def f2(driver):
    url = driver.current_url
    try:
        locator = (By.XPATH, "(//font[@class='currentpostionfont'])[last()]")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        driver.find_element_by_xpath("(//td[@class='LeftMenuJsgc'])[{}]".format(3)).click()
        try:
            locator = (By.XPATH, "(//font[@class='currentpostionfont'])[last()][string()!='%s']" % val)
            WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator))
        except:
            driver.refresh()
            time.sleep(2)

        locator = (By.XPATH, "//td[@class='huifont']")
        str = WebDriverWait(driver, 5).until(EC.presence_of_element_located(locator)).text
        num = int(re.findall(r'/(\d+)', str)[0])
    except:
        html_data = driver.page_source
        if "本栏目暂时没有内容" in html_data:
            num = 1
        else:
            num = 1
    driver.quit()
    return num



def f3(driver, url):
    driver.get(url)

    locator = (By.CLASS_NAME, "top-banner")

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

    div = soup.find('td', style="padding-top:20px;")

    div=div.find_all('tr')

    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071001/071001001/071001001001/",
     ["name", "ggstart_time", "href", "info"],f1,f2],


    ["gcjs_biangeng_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071001/071001002/071001002001/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zsjg_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071001/071001003/071001003001/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071001/071001004/071001004001/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiao_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071001/071001005/071001005001/",
     ["name", "ggstart_time", "href", "info"],f1,f2],


    ["gcjs_xiaoer_zhaobiao_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071001/071001006/071001006001/071001006001001/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_xiaoer_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071001/071001006/071001006002/071001006002001/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_xiaoer_zhongbiao_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071001/071001006/071001006003/071001006003001/",
     ["name", "ggstart_time", "href", "info"],f1,f2],


    ["zfcg_zhaobiao_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071002/071002002/071002002001/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_biangeng_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071002/071002003/071002003001/",
     ["name", "ggstart_time", "href", "info"],f1,f2],



    ["zfcg_zhongbiao_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071002/071002005/071002005001/",
     ["name", "ggstart_time", "href", "info"],f1,f2],


    ["qsy_zhaobiao_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071005/071005001/071005001001/",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["qsy_gqita_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071005/071005002/071005002001/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="浙江省龙泉市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.4.175","zhejiang","longquan"])


    # driver=webdriver.Chrome()
    # url="http://www.lssggzy.com/lsweb/jyxx/071001/071001001/071001001001/"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    # # driver = webdriver.Chrome()
    # # url = "http://www.jhztb.gov.cn/jhztb/gcjyysgs/index.htm"
    # # driver.get(url)
    # for i in range(13, 16):
    #     df=f1(driver, i)
    #     print(df)
