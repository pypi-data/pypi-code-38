import json
import math
import re
from datetime import datetime,timedelta
import requests
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong3.util.etl import est_html, est_meta
import time
import random
import fake_useragent 
_name_ = 'heilongjiang_haerbin'

'''
由于本网站数据量大，线程容易失败，现在 分年分页 爬取数据。
'''
fakeUA = fake_useragent.fake.UserAgent()
date_pageNum = []

def f1(driver, num):

    for i ,pageNum in enumerate(date_pageNum):

        if num - pageNum<=0:
            if WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'tbx_Start'))).get_attribute('value') != datetime.strftime(date_list[i][0], '%Y-%m-%d'):
                jump_date(driver,date_list[i])
            break
        else:num-=pageNum

    # print('页码:',num)
    locator = (By.XPATH, "//td[@colspan='4']/table[@border='0']")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath("//td[@colspan='4']/table[@border='0']//span").text
    locator = (By.XPATH, '//table[@id="GV_Data"]/tbody/tr')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//table[@id="GV_Data"]/tbody/tr[@style="height:22px;"][1]/td[2]/a').text

    if int(cnum) != int(num):
        #这个js作用范围只能在页面内能看到的页码。
        #因此需要进行跳页
        first_page = driver.find_element_by_xpath('//td[@colspan="4"]//tr/td[2]').text
        while int(num) - int(first_page) > 9:

            driver.find_element_by_xpath('//td[@colspan="4"]//tr/td[last()]').click()
            WebDriverWait(driver,20).until(EC.visibility_of_element_located((By.XPATH,'//td[@colspan="4"]//tr')))
            first_page = driver.find_element_by_xpath('//td[@colspan="4"]//tr/td[2]').text

        while int(first_page) > int(num) and int(first_page)>10:

            driver.find_element_by_xpath('//td[@colspan="4"]//tr/td[1]').click()
            first_page = driver.find_element_by_xpath('//td[@colspan="4"]//tr/td[2]').text
            WebDriverWait(driver,20).until(EC.visibility_of_element_located((By.XPATH,'//td[@colspan="4"]//tr')))
        cnum = driver.find_element_by_xpath("//td[@colspan='4']/table[@border='0']//span").text
        if int(cnum) != int(num):
            driver.execute_script("javascript:__doPostBack('GV_Data','Page$%s')"%num)

        locator = (By.XPATH, '//table[@id="GV_Data"]/tbody/tr[@style="height:22px;"][1]/td[2]/a[not(contains(text(),"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))


    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@id="GV_Data"]/tbody/tr[@style="height:22px;"]')

    driver_info = webdriver.DesiredCapabilities.CHROME

    if "--proxy" in driver_info['goog:chromeOptions']['args'][0]:

        proxy_ip = driver_info['goog:chromeOptions']['args'][0].split('=')[1].split('://')
        proxies = {proxy_ip[0]: proxy_ip[1]}
    else:
        proxies = {}
    EVENTVALIDATION =  body.xpath('//input[@id="__EVENTVALIDATION"]/@value')
    VIEWSTATE =  body.xpath('//input[@id="__VIEWSTATE"]/@value')
    headlers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'www.hrbjjzx.cn',
        'Origin': 'http://www.hrbjjzx.cn',
        'Referer': driver.current_url,
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': fakeUA.random }

    for i,content in enumerate(content_list):
        id = content.xpath('.//a/@href')[0].strip()
        id = re.findall(r"'([^']+?)'",id)[0]

        param = {
            '__EVENTTARGET': id,
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': VIEWSTATE,
            '__VIEWSTATEENCRYPTED': '',
            '__EVENTVALIDATION': EVENTVALIDATION,
            'tbx_Content': '--标题关键字--',
            'ddl_Type': '全部',
            'tbx_Start': '',
            'tbx_End': '', }

        name = content.xpath("./td[2]/a/text()")[0].strip()
        try:
            try:
                headers = requests.post(driver.current_url,data=param ,allow_redirects=False,headers=headlers,timeout=40).headers
            except:
                headers = requests.post(driver.current_url,data=param,allow_redirects=False,proxies=proxies,headers=headlers,timeout=40).headers
        except:
            time.sleep(random.randint(2,5))
            headers = requests.post(driver.current_url, data=param, allow_redirects=False, headers=headlers,timeout=40).headers

        url = 'http://www.hrbjjzx.cn' + headers['location']
        ggstart_time = content.xpath("./td[4]/text()")[0].strip()

        ggtype = content.xpath("./td[3]/text()")[0].strip()

        info = json.dumps({"type":ggtype},ensure_ascii=False)
        temp = [name, ggstart_time,url,info]
        data.append(temp)
        #print(temp)
    df = pd.DataFrame(data=data)

    return df

def jump_date(driver,date):
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'tbx_Start'))).clear()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'tbx_End'))).clear()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'tbx_Start'))).send_keys(datetime.strftime(date[0], '%Y-%m-%d'))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'tbx_End'))).send_keys(datetime.strftime(date[1], '%Y-%m-%d'))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'ibSearch'))).click()

def f2(driver):
    total_page = 0
    locator = (By.XPATH, '//span[@id="lbl_Title"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    for date in date_list:
        jump_date(driver,date)
        items = driver.find_element_by_id('lbl_Title').text
        page = math.ceil(int(items)/15)
        date_pageNum.append(page)
        total_page+=page

    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//*[@id="main_box"]/table/tbody/tr[4]/td/table/tbody//table')
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
    soup = BeautifulSoup(page, 'lxml')
    div = soup.find('table', bgcolor='#A2D2F6')
    return div


def get_url(driver,i):
    driver.execute_script("javascript:__doPostBack('GV_Data$ctl%s$LinkButton1','')"%('0'+str(i+2) if i+2 <10 else str(i+2)))
    locator = (By.XPATH, '//*[@id="main_box"]/table/tbody/tr[4]/td/table/tbody//table')
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    url = driver.current_url
    driver.back()
    return url





def get_date():
    date_list = []
    start_date,end_date = datetime(2000,1,1),datetime(2010,1,1)
    tmp=[start_date,end_date]
    date_list.append(tmp)
    while end_date < datetime.now():
        start_date,end_date = end_date ,start_date
        end_date = start_date.replace(year=start_date.year+1)
        # print('start',datetime.strftime(start_date, '%Y-%m-%d'), 'end',datetime.strftime(end_date, '%Y-%m-%d'))
        tmp=[start_date,end_date]
        date_list.insert(0,tmp)
    return date_list


    # driver.find_element_by_id('tbx_Start')


data = [
    ["gcjs_gqita_zhao_bian_liu_gg",
     "http://www.hrbjjzx.cn/Search.aspx?st=--标题关键字--&t=4",
     ["name", "ggstart_time", "href","info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://www.hrbjjzx.cn/Search.aspx?st=--标题关键字--&t=5",
     ["name", "ggstart_time", "href","info"], f1, f2],
]

def work(conp, **args):
    est_meta(conp, data=data, diqu="黑龙江省哈尔滨市", **args)
    est_html(conp, f=f3, **args)

date_list = get_date()

if __name__ == "__main__":

    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "heilongjiang_haerbin"]
    work(conp)
    #driver = webdriver.Chrome()
    #driver.get()
    # driver = webdriver.Chrome()

    # driver.get("http://www.hrbjjzx.cn/Search.aspx?st=--%E6%A0%87%E9%A2%98%E5%85%B3%E9%94%AE%E5%AD%97--&t=4")
    # f2(driver)
    # f1(driver,1147)
    # f1(driver,905)
    # f1(driver,93)
    # f1(driver,94)
    # f1(driver,101)
    # f1(driver,97)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://www.hrbjjzx.cn/Bid_Front/TenderContent.aspx?ID=33107'))
    # driver.close()
    # print(date_pageNum)
    # print(date_list)