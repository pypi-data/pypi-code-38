
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

from zhulong.util.etl import add_info,est_meta,est_html,est_tbs,add_info


_name_="fujian"





def f1(driver, num):
    locator = (By.XPATH, "//div[@class='article-list-template']/a[1]")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-9:]
    locator = (By.XPATH, "//ul[@class='pagination']/li[@class='active']/a")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = int(st)
    url = driver.current_url
    if num != int(cnum):
        if "page" not in url:
            s = "?page=%d" % (num) if num > 1 else "?page=1"
            url = url + s
        elif num == 1:
            url = re.sub("page=[0-9]*", "page=1", url)
        else:
            s = "page=%d" % (num) if num > 1 else "page=1"
            url = re.sub("page=[0-9]*", s, url)
        driver.get(url)
        locator = (By.XPATH, "//div[@class='article-list-template']/a[1][not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("div", class_="article-list-template")
    trs = table.find_all("a")
    data = []
    for tr in trs:
        try:
            title = tr["title"].strip()
        except:
            title = tr.find("span", class_='article-list-text').text.strip()
        href = tr["href"]
        if 'http' in href:
            link = href
        else:
            link = "http://www.fjggzyjy.cn" + href.strip()
        td = tr.find("span", class_='article-list-date').text.strip()
        try:
            xm_num = tr.find("span", class_='article-list-number').span.text.strip()
        except:
            xm_num = ''
        info = json.dumps({'xm_num':xm_num}, ensure_ascii=False)
        tmp = [title, td, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='article-list-template']/a[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//a[@class='end']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = int(str)
        driver.quit()
        return int(num)
    except:
        driver.quit()
        return 1 



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='layout-article'][string-length()>30]")
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
    div = soup.find('div', class_="layout-article")
    return div


data = [
    ["gcjs_zhaobiao_fangjian_gg",
     "http://www.fjggzyjy.cn/news/category/46/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':"房屋建设"}),f2],

    ["gcjs_gqita_bian_bu_liu_fangjian_gg",
     "http://www.fjggzyjy.cn/news/category/48/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':"房屋建设"}), f2],


    ["gcjs_zhongbiaohx_fangjian_gg",
     "http://www.fjggzyjy.cn/news/category/49/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':"房屋建设"}),f2],

    ["gcjs_zhongbiao_fangjian_gg",
     "http://www.fjggzyjy.cn/news/category/50/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':"房屋建设"}),f2],

    ["gcjs_zhaobiao_jiaotong_gg",
     "http://www.fjggzyjy.cn/news/category/52/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':"交通工程"}), f2],

    ["gcjs_gqita_bian_bu_liu_jiaotong_gg",
     "http://www.fjggzyjy.cn/news/category/54/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':"交通工程"}), f2],

    ["gcjs_zhongbiaohx_jiaotong_gg",
     "http://www.fjggzyjy.cn/news/category/55/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':"交通工程"}),f2],

    ["gcjs_zhongbiao_jiaotong_gg",
     "http://www.fjggzyjy.cn/news/category/56/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':"交通工程"}),f2],

    ["zfcg_zhaobiao_gg",
     "http://www.fjggzyjy.cn/news/category/10/",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_biangeng_gg",
     "http://www.fjggzyjy.cn/news/category/11/",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_gqita_zhong_liu_gg",
     "http://www.fjggzyjy.cn/news/category/12/",
    ["name", "ggstart_time", "href", "info"],f1,f2],


    ["zfcg_zhaobiao_wsjj_gg",
     "http://www.fjggzyjy.cn/news/category/14/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':"网上竞价"}), f2],

    ["zfcg_gqita_bian_bu_wsjj_gg",
     "http://www.fjggzyjy.cn/news/category/78/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':"网上竞价"}), f2],

    ["zfcg_zhongbiao_wsjj_gg",
     "http://www.fjggzyjy.cn/news/category/16/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':"网上竞价"}), f2],

    ["zfcg_gqita_zhong_liu_wsjj_gg",
     "http://www.fjggzyjy.cn/news/category/16/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':"网上竞价"}), f2],

    ["zfcg_gqita_zhao_zhong_bian_gg",
     "http://www.fjggzyjy.cn/news/category/17/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_zhaobiao_gg",
     "http://www.fjggzyjy.cn/news/category/58/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_gqita_liu_bian_bu_gg",
     "http://www.fjggzyjy.cn/news/category/60/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_zhongbiaohx_gg",
     "http://www.fjggzyjy.cn/news/category/61/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_zhongbiao_gg",
     "http://www.fjggzyjy.cn/news/category/62/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]



def work(conp,**args):
    est_meta(conp,data=data,diqu="福建省省级",**args)
    est_html(conp,f=f3,**args)


# if __name__=='__main__':
#     work(conp=["postgres","since2015","192.168.4.175","fujian","fujian"])

# url="http://www.fjggzyjy.cn/news/category/78/"


# driver=webdriver.Chrome()

# driver.get(url)

