import json
import math
import random
import re
from datetime import datetime,timedelta
import requests
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong4.util.etl import est_html, est_meta, add_info
import time
from zhulong4.util.fake_useragent import UserAgent
_name_ = 'b2b_10086_cn'

UA = UserAgent()
headers = {
    'Referer': 'https://b2b.10086.cn/b2b/main/listVendorNotice.html?noticeType=2',
    'User-Agent': UA.random,
}
dataparams = {
    'page.currentPage': 1,
    'page.perPageSize': 20,
    'noticeBean.sourceCH': '',
    'noticeBean.source': '',
    'noticeBean.title': '',
    'noticeBean.startDate': '',
    'noticeBean.endDate': '',
}
proxy = {}

def get_ip():
    global proxy
    try:
        url = """http://ip.11jsq.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=0&fa=0&fetch_key=&qty=1&time=1&pro=&city=&port=1&format=txt&ss=1&css=&dt=1&specialTxt=3&specialJson="""
        r = requests.get(url)
        time.sleep(1)

        ip = r.text
        proxy = {'http': ip}
    except:

        proxy = {}
    # print('get_ip ',proxy)
    return proxy
get_ip()


def f1(driver, num):
    if "preShowBiao" in driver.current_url:

        locator = (By.XPATH, '//table[@class="jtgs_table"]/tbody/tr[@style="width:100%;" or @style="width: 100%;" or @style="width:100%"]')
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        val = driver.find_element_by_xpath('//table[@class="jtgs_table"]/tbody/tr[@style="width:100%;" or @style="width: 100%;" or @style="width:100%"]').get_attribute("onclick")[-15:]
        try:
            cnum = driver.find_element_by_xpath('//a[@class="current"]/span').text
        except:
            cnum = driver.find_element_by_xpath('//a[@class="current"]').text
        if int(cnum) != int(num):
            driver.execute_script('gotoPage(%s);'%num)
            locator = (By.XPATH, '''//table[@class="jtgs_table"]/tbody/tr[@style="width:100%%;" or @style="width: 100%%;" or @style="width:100%%"][not(contains(@onclick,"%s"))]''' % val)
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
        data = []
        page = driver.page_source
        body = etree.HTML(page)
        content_list = body.xpath('//table[@class="jtgs_table"]/tbody/tr[@style="width:100%;" or @style="width: 100%;" or @style="width:100%"]')
        for content in content_list:
            name = content.xpath("./td/a/text()")[0].strip()
            url = "https://b2b.10086.cn/b2b/main/viewNoticeContent.html?noticeBean.id=" + re.findall("\'([^\']+)\'",content.xpath("./@onclick")[0])[0]

            day, hour, minute = re.findall('(\d+)天(\d+)时(\d+)分', content.xpath("./td[last()]")[0].xpath("string(.)"))[0]
            ggstart_time = (datetime.now()+ timedelta(days=int(day),hours=int(hour),minutes=int(minute))).strftime('%Y-%m-%d %H:%M:%S')
            info = json.dumps({'info':'距离标书售卖截止时间'},ensure_ascii=False)
            temp = [name, ggstart_time, url,info]
            data.append(temp)

        df = pd.DataFrame(data=data)
    else:
        driver_info = webdriver.DesiredCapabilities.CHROME
        data_param = dataparams.copy()
        data_param['page.currentPage'] = num
        try:
            if "--proxy" in driver_info['goog:chromeOptions']['args'][0]:
                proxy_ip = driver_info['goog:chromeOptions']['args'][0].split('=')[1].split('://')
                proxies = {proxy_ip[0]: proxy_ip[1]}
                page = requests.post(driver.current_url, headers=headers, data=data_param, proxies=proxies, timeout=40).text
            else:
                page = requests.post(driver.current_url, headers=headers, data=data_param, timeout=40).text
        except:
            try:
                # print(proxy)
                page = requests.post(driver.current_url, headers=headers, data=data_param,proxies=proxy, timeout=40).text
            except:
                get_ip()
                page = requests.post(driver.current_url, headers=headers, data=data_param,proxies=proxy, timeout=40).text


        data = []
        body = etree.HTML(page)
        content_list = body.xpath('//table[@class="zb_result_table"]/tr[position()!=1 and position()!=2]')

        for content in content_list:
            url = "https://b2b.10086.cn/b2b/main/viewNoticeContent.html?noticeBean.id=" + re.findall("\'([^\']+)\'", content.xpath("./@onclick")[0])[0]
            ggstart_time = content.xpath("./td[last()]/text()")[0]
            try:
                name = content.xpath("./td[3]/a/@title")[0].strip()
            except :
                name = content.xpath('./td[3]/a/text()')[0].strip()

            temp = [name, ggstart_time, url]
            data.append(temp)
            # print(temp)
        df = pd.DataFrame(data=data)
        df['info'] = None
    return df


def f2(driver):
    if "preShowBiao" in driver.current_url:

        driver.maximize_window()
        locator = (By.XPATH, '//*[@id="pageid2"]')
        driver.execute_script("window.scrollBy(0,document.body.scrollHeight)", "")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        sign1 = driver.find_element_by_xpath('//*[@id="pageid2"]/table/tbody/tr/td[5]/a/span|//*[@id="pageid2"]/table//td[last()]//span').text
        if sign1 == '尾页':
            total_temp = driver.find_element_by_xpath('//*[@id="pageid2"]/table/tbody/tr/td[5]/a').get_attribute('onclick')
            total_page = re.findall(r'(\d+)',total_temp)[0]
        else:
            while 1:
                time.sleep(0.5)
                element = driver.find_element_by_xpath('//*[@id="pageid2"]/table//td[last()]//span')
                # print(element.is_enabled())
                if element.is_displayed():

                    driver.find_element_by_xpath('//*[@id="pageid2"]/table//td[last()]//span').click()
                else:
                    total_page = driver.find_element_by_xpath('//*[@id="pageid2"]/table//td[last()-1]/a[last()]/span').text
                    break


    else:
        driver_info = webdriver.DesiredCapabilities.CHROME
        try:
            if "--proxy" in driver_info['goog:chromeOptions']['args'][0]:

                proxy_ip = driver_info['goog:chromeOptions']['args'][0].split('=')[1].split('://')
                proxies = {proxy_ip[0]: proxy_ip[1]}
                page = requests.post(driver.current_url, headers=headers, data=dataparams, proxies=proxies, timeout=40).text
            else:
                page = requests.post(driver.current_url, headers=headers, data=dataparams, proxies=get_ip(),timeout=40).text
        except:
            page = requests.post(driver.current_url, headers=headers, data=dataparams, timeout=40).text
        body = etree.HTML(page)
        total_page = re.findall(r'\d+',body.xpath('//td[@id="pageid2"]//td[last()]/a/@onclick')[0])[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):

    driver.get(url)
    locator = (By.XPATH, '//table[@class="zb_table"]')
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
    div = soup.find('table', class_='zb_table')
    return div


data = [
    ["qy_zhaobiao_1_gg",
     "https://b2b.10086.cn/b2b/main/showBiao!preShowBiao.html?noticeType=list1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"Tag":"正在招标"}), f2],

    ["qy_kaibiao_gg",
     "https://b2b.10086.cn/b2b/main/showBiao!preShowBiao.html?noticeType=list2",
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{"Tag":"即将开标"}), f2],
    ["qy_zhongbiaohx1_gg",
     "https://b2b.10086.cn/b2b/main/showBiao!preShowBiao.html?noticeType=list3",
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{"Tag":"正在候选人公示"}), f2],

    ["qy_zhaobiao_gg",
     "https://b2b.10086.cn/b2b/main/listVendorNoticeResult.html?noticeBean.noticeType=2",
     ["name", "ggstart_time", "href",  "info"], f1, f2],

    ["qy_zgys_gg",
     "https://b2b.10086.cn/b2b/main/listVendorNoticeResult.html?noticeBean.noticeType=3",
     ["name", "ggstart_time", "href",  "info"], f1, f2],
    ["qy_zhongbiaohx_gg",
     "https://b2b.10086.cn/b2b/main/listVendorNoticeResult.html?noticeBean.noticeType=7",
     ["name", "ggstart_time", "href",  "info"], f1, f2],

    ["qy_zhongbiao_gg",
     "https://b2b.10086.cn/b2b/main/listVendorNoticeResult.html?noticeBean.noticeType=16",
     ["name", "ggstart_time", "href",  "info"], f1, f2],
    ["qy_zhaobiao_dyly_gg",
     "https://b2b.10086.cn/b2b/main/listVendorNoticeResult.html?noticeBean.noticeType=1",
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{"method":"单一来源"}), f2],
    ["qy_gqita_info_gg",
     "https://b2b.10086.cn/b2b/main/listVendorNoticeResult.html?noticeBean.noticeType=8",
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{"Tag":"供应商信息收集公告"}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="中国移动采购与招标网", **args)
    est_html(conp, f=f3, **args)




if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang_qiye", "b2b_10086_cn"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get('https://b2b.10086.cn/b2b/main/showBiao!preShowBiao.html?noticeType=list1')
    # f1(driver,1)
    # driver.get('https://b2b.10086.cn/b2b/main/showBiao!preShowBiao.html?noticeType=list2')
    # f1(driver,1)
    # driver.get('https://b2b.10086.cn/b2b/main/showBiao!preShowBiao.html?noticeType=list3')
    # f1(driver,1)