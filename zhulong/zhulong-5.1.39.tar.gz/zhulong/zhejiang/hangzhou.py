import random
import pandas as pd
import re
import requests
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
from zhulong.util.fake_useragent import UserAgent
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs


_name_="hangzhou"




def f1(driver, num):
    proxies_data = webdriver.DesiredCapabilities.CHROME
    proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
    if proxies_chromeOptions:
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s'% proxy}
    else:
        proxies = {}
    url = driver.current_url
    afficheType = re.findall(r'afficheType=(\d+)', url)[0]
    start_url = 'http://www.hzctc.cn/SecondPage/GetNotice'
    payloadData = {
        'area': '',
        'afficheType': afficheType,
        'IsToday': '',
        'title': '',
        'proID': '',
        'number': '',
        '_search': 'false',
        # 'nd': '1544528549866',
        'rows': '10',
        'page': '{}'.format(num),
        'sidx': 'PublishStartTime',
        'sord': 'desc',
    }
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent,
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'www.hzctc.cn',
    }
    if proxies:
        res = requests.post(url=start_url, headers=headers, data=payloadData, proxies=proxies)
    else:
        res = requests.post(url=start_url, headers=headers, data=payloadData)
    # 需要判断是否为登录后的页面
    data_list = []
    time.sleep(1)
    if res.status_code == 200:
        html = res.text
        if html:
            html = json.loads(html)
            datalist = html["rows"]
            for data in datalist:
                projName = data['TenderName']
                publishTime = data['PublishStartTime']
                publishTime = re.findall(r'(\d+-\d+-\d+)', publishTime)[0]
                if afficheType == '486':
                    link = "http://www.hzctc.cn/OpenBidRecord/Index?id=" + data['ID'] + "&tenderID=" + data['TenderID'] + "&ModuleID=" + "{}".format(afficheType)
                else:
                    link = "http://www.hzctc.cn/AfficheShow/Home?AfficheID=" + data['ID'] + "&IsInner=" + "{}".format(data['IsInner']) + "&ModuleID=" + "{}".format(afficheType)
                info = {}
                if data['CodeName']:
                    info['diqu'] = data['CodeName']
                if data['PublishEndTime']:
                    info['PublishEndTime'] = re.findall(r'(\d+-\d+-\d+)', data['PublishEndTime'])[0]
                if info:info = json.dumps(info, ensure_ascii=False)
                else:info = None
                tmp = [projName, publishTime, link, info]
                data_list.append(tmp)
    df = pd.DataFrame(data_list)
    return df



def f2(driver):
    url = driver.current_url
    afficheType = re.findall(r'afficheType=(\d+)', url)[0]
    start_url = 'http://www.hzctc.cn/SecondPage/GetNotice'
    payloadData = {
        'area': '',
        'afficheType': afficheType,
        'IsToday': '',
        'title': '',
        'proID': '',
        'number': '',
        '_search': 'false',
        # 'nd': '1544528549866',
        'rows': '10',
        'page': '1',
        'sidx': 'PublishStartTime',
        'sord': 'desc',
    }
    num = get_pageall(start_url, payloadData)
    driver.quit()
    return num


def get_pageall(url, payloadData):
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent,
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'www.hzctc.cn',
        }
    sesion = requests.session()
    res = sesion.post(url=url, headers=headers, data=payloadData)
    # 需要判断是否为登录后的页面
    time.sleep(1)
    if res.status_code == 200:
        html = res.text
        if html:
            html = json.loads(html)
            total = html["total"]
            return total


def f3(driver, url):
    driver.get(url)
    if "信息当前尚未发布或发布已截止" in driver.page_source:
        return 404
    locator = (By.XPATH, "//div[@class='MainList'][string-length()>40]")
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
    div = soup.find('div', class_='MainList')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.hzctc.cn/SecondPage/ProjectAfficheList?area=&afficheType=22",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_kaibiao_gg",
     "http://www.hzctc.cn/SecondPage/ProjectAfficheList?area=&afficheType=486",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.hzctc.cn/SecondPage/ProjectAfficheList?area=&afficheType=25",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiao_gg",
     "http://www.hzctc.cn/SecondPage/ProjectAfficheList?area=&afficheType=28",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhaobiao_gg",
     "http://www.hzctc.cn/SecondPage/ProjectAfficheList?area=&afficheType=27",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhaobiao_danyilaiyuan_gg",
     "http://www.hzctc.cn/SecondPage/ProjectAfficheList?area=&afficheType=26",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'单一来源'}), f2],

    ["zfcg_biangeng_gg",
     "http://www.hzctc.cn/SecondPage/ProjectAfficheList?area=&afficheType=29",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_gqita_zhong_liu_gg",
     "http://www.hzctc.cn/SecondPage/ProjectAfficheList?area=&afficheType=32",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["qsy_zhaobiao_gg",
     "http://www.hzctc.cn/SecondPage/ProjectAfficheList?area=&afficheType=34",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'综合其他'}),f2],

    ["qsy_zhongbiaohx_gg",
     "http://www.hzctc.cn/SecondPage/ProjectAfficheList?area=&afficheType=37",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'综合其他'}),f2],
]



def work(conp,**args):
    est_meta(conp,data=data,diqu="浙江省杭州市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","zhejiang","hangzhou"])

