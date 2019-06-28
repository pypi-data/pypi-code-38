import lxml
import random
import pandas as pd
import re
import requests
from lxml import etree
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
from html.parser import HTMLParser
import json



from zhulong.util.etl import add_info,est_meta,est_html,est_tbs

_name_="sichuan"


def f1(driver, num):
    url = driver.current_url
    val = driver.find_element_by_xpath('//pre').text.strip()
    html_json = json.loads(val)
    html_data = html_json['data']
    html_data = json.loads(html_data)
    html_link_1 = html_data[0]['Link']
    cnum = re.findall(r'page=(\d+)', url)[0]
    if num != int(cnum):
        if "page" not in url:
            s = "&page=%d" % (num) if num > 1 else "&page=1"
            url = url + s
        elif num == 1:
            url = re.sub("page=[0-9]*", "page=1", url)
        else:
            s = "page=%d" % (num) if num > 1 else "page=1"
            url = re.sub("page=[0-9]*", s, url)
        driver.get(url)
        locator = (By.XPATH, "//pre[not(contains(text(), '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        val = driver.find_element_by_xpath('//pre').text.strip()
        html_json = json.loads(val)
        html_data = html_json['data']
        html_data = json.loads(html_data)
        html_link_2 = html_data[0]['Link']
        if html_link_1 == html_link_2:
            raise TimeoutError
    data_list = []
    for data in html_data:
        title = data['Title']
        td = data['CreateDateStr']
        link = "http://58.87.81.13"+data['Link']
        info = {}
        if data['username']: info['diqu'] = data['username']
        if data['TableName']: info['xxlx'] = data['TableName']
        if data['businessType']: info['ywlx'] = data['businessType']
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:
            info = None
        tmp = [title, td, link, info]
        data_list.append(tmp)
    df = pd.DataFrame(data_list)
    return df


def f2(driver):
    locator = (By.XPATH, "/html/body/pre")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//pre').text
    html_json = json.loads(val)
    if '暂无相关数据' in html_json['message']:
        return 0
    num = html_json['pageCount']
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    time.sleep(2)
    locator = (By.XPATH, "//div[@class='Nmds' and @style='display: block;'][string-length()>40]")
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
    div = soup.find('div', attrs={'class':'Nmds', 'style':'display: block;'})
    return div



timesEnd = time.strftime('%Y-%m-%d',time.localtime(time.time()))

data = [
    ["gcjs_zhaobiao_gg",
     "http://58.87.81.13/Info/GetInfoListNew?keywords=&times=6&timesStart=2016-11-26&timesEnd={}&province=&area=&businessType=project&informationType=TenderAnnQuaInqueryAnn&industryType=&page=1&parm=".format(timesEnd),
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zgys_gg",
     "http://58.87.81.13/Info/GetInfoListNew?keywords=&times=6&timesStart=2016-11-26&timesEnd={}&province=&area=&businessType=project&informationType=QualiInqueryClari&industryType=&page=1&parm=".format(timesEnd),
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://58.87.81.13/Info/GetInfoListNew?keywords=&times=6&timesStart=2016-11-26&timesEnd={}&province=&area=&businessType=project&informationType=TenderFileClariModi&industryType=&page=1&parm=".format(timesEnd),
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_liu_zhongz_gg",
     "http://58.87.81.13/Info/GetInfoListNew?keywords=&times=6&timesStart=2016-11-26&timesEnd={}&province=&area=&businessType=project&informationType=TenderStreams&industryType=&page=1&parm=".format(timesEnd),
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_kaibiao_gg",
     "http://58.87.81.13/Info/GetInfoListNew?keywords=&times=6&timesStart=2016-11-26&timesEnd={}&province=&area=&businessType=project&informationType=BidOpenRecord&industryType=&page=1&parm=".format(timesEnd),
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://58.87.81.13/Info/GetInfoListNew?keywords=&times=6&timesStart=2016-11-26&timesEnd={}&province=&area=&businessType=project&informationType=TenderCandidateAnnounce&industryType=&page=1&parm=".format(timesEnd),
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_hetong_gg",
     "http://58.87.81.13/Info/GetInfoListNew?keywords=&times=6&timesStart=2016-11-26&timesEnd={}&province=&area=&businessType=project&informationType=ContractPerformance&industryType=&page=1&parm=".format(timesEnd),
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://58.87.81.13/Info/GetInfoListNew?keywords=&times=6&timesStart=2016-11-26&timesEnd={}&province=&area=&businessType=purchase&informationType=PurchaseBulletin&industryType=&page=1&parm=".format(timesEnd),
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://58.87.81.13/Info/GetInfoListNew?keywords=&times=6&timesStart=2016-11-26&timesEnd={}&province=&area=&businessType=purchase&informationType=PurchaseTermination&industryType=&page=1&parm=".format(timesEnd),
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_zhong_liu_gg",
     "http://58.87.81.13/Info/GetInfoListNew?keywords=&times=6&timesStart=2016-11-26&timesEnd={}&province=&area=&businessType=purchase&informationType=PurchaseBid&industryType=&page=1&parm=".format(timesEnd),
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_hetong_gg",
     "http://58.87.81.13/Info/GetInfoListNew?keywords=&times=6&timesStart=2016-11-26&timesEnd={}&province=&area=&businessType=purchase&informationType=PurchaseContract&industryType=&page=1&parm=".format(timesEnd),
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_zhaobiao_gg",
     "http://58.87.81.13/Info/GetInfoListNew?keywords=&times=6&timesStart=2016-11-26&timesEnd={}&province=&area=&businessType=othertrade&informationType=OtherTradePubInfo&industryType=&page=1&parm=".format(timesEnd),
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gglx':'其他类别'}), f2],

    ["qsy_gqita_zhong_liu_gg",
     "http://58.87.81.13/Info/GetInfoListNew?keywords=&times=6&timesStart=2016-11-26&timesEnd={}&province=&area=&businessType=othertrade&informationType=OtherTradeResultInfo&industryType=&page=1&parm=".format(timesEnd),
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gglx':'其他类别'}), f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省省级",**args)
    est_html(conp,f=f3,**args)



if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","sichuan","sichuan"])


# 修改日期：2019/5/16
# 网址更替：http://58.87.81.13/Info/Index/project.html
