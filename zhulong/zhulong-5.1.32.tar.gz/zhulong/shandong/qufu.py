import json
import random
import time
import pandas as pd
import re
import requests
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
from zhulong.util.etl import est_meta, est_html, add_info
from zhulong.util.fake_useragent import UserAgent

_name_="qufu"


def f1(driver, num):
    url = driver.current_url
    id = re.findall(r'CategoryCode=(\d+)', url)[0]
    datas = get_data(id, num)
    df = pd.DataFrame(data=datas)
    return df


def get_data(id, num):
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    start_url = "http://www.jnggzyjy.gov.cn/api/services/app/stPrtBulletin/GetBulletinList"

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': user_agent,
        # 'Cookie':'Abp.Localization.CultureName=zh-CN; ASP.NET_SessionId=m1131mz3oijy0szk04qoe5j2; __RequestVerificationToken=M3w3qWf_PisGP3Oria-7xQ3pf6Ip3u0w08xBjbZPXTYX5VUgZE7Ty0zBMO_1zXciYHfFsHVbY-oir7etbDRXXlTMaqNLM1UzIwEAoEbC9Kw1; Public-XSRF-TOKEN=-RSVwuDUYfSxBv8HxRN5yAaA4VM3PAto-H-1Hc1kDxQFVTMyvzfDS1zc2a_1OcB8Jmne3HMDkwPalWXI6l0xOOiMX2ni8vCB1-tfyDJf0YQ1; UM_distinctid=166c4886295f5-0a362c74ecbee4-68101b7d-1fa400-166c4886296273; CNZZDATA1273473557=160814158-1540890505-%7C1540890505',
        'Host':'www.jnggzyjy.gov.cn',
        'Public-X-XSRF-TOKEN':'-RSVwuDUYfSxBv8HxRN5yAaA4VM3PAto-H-1Hc1kDxQFVTMyvzfDS1zc2a_1OcB8Jmne3HMDkwPalWXI6l0xOOiMX2ni8vCB1-tfyDJf0YQ1',
    }
    payloadData = {
        "FilterText": "",
        "categoryCode": "{}".format(id),
        "maxResultCount": 20,
        "skipCount": (num - 1) * 20,
        "tenantId": "11",
    }
    timeOut = 25
    dumpJsonData = json.dumps(payloadData)
    sesion = requests.session()
    res = sesion.post(url=start_url, headers=headers, data=dumpJsonData, timeout=timeOut)
    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        html = res.text
        datas = []
        if html:
            # print(type(html))
            html = json.loads(html)
            data = html["result"]
            table = data["items"]
            for data_dict in table:

                td_2 = data_dict["id"]
                td_3 = data_dict["releaseDate"]
                try:
                    date_l = re.findall(r'(\d+.*)T', td_3)[0]
                except:
                    date_l = td_3
                td_4 = data_dict["title"]
                td_5 = data_dict["categoryCode"]
                # "http://www.jnggzyjy.gov.cn/JiNing/Bulletins/Detail/566846de-c45d-b4e9-2aef-39e8497e4baa/?CategoryCode=511001"
                prjName_link = "http://www.jnggzyjy.gov.cn/JiNing/Bulletins/Detail/" + td_2 + "/?CategoryCode=" + td_5
                info = None
                data = [td_4, date_l, prjName_link, info]
                datas.append(data)
        return datas



def f2(driver):
    start_url = driver.current_url
    id = re.findall(r'CategoryCode=(\d+)', start_url)[0]
    driver.quit()
    page_num = get_pageall(id)
    return int(page_num)


def get_pageall(id):
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    start_url = "http://www.jnggzyjy.gov.cn/api/services/app/stPrtBulletin/GetBulletinList"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': user_agent,
        # 'Cookie':'Abp.Localization.CultureName=zh-CN; ASP.NET_SessionId=m1131mz3oijy0szk04qoe5j2; __RequestVerificationToken=M3w3qWf_PisGP3Oria-7xQ3pf6Ip3u0w08xBjbZPXTYX5VUgZE7Ty0zBMO_1zXciYHfFsHVbY-oir7etbDRXXlTMaqNLM1UzIwEAoEbC9Kw1; Public-XSRF-TOKEN=-RSVwuDUYfSxBv8HxRN5yAaA4VM3PAto-H-1Hc1kDxQFVTMyvzfDS1zc2a_1OcB8Jmne3HMDkwPalWXI6l0xOOiMX2ni8vCB1-tfyDJf0YQ1; UM_distinctid=166c4886295f5-0a362c74ecbee4-68101b7d-1fa400-166c4886296273; CNZZDATA1273473557=160814158-1540890505-%7C1540890505',
        'Host':'www.jnggzyjy.gov.cn',
        'Public-X-XSRF-TOKEN':'-RSVwuDUYfSxBv8HxRN5yAaA4VM3PAto-H-1Hc1kDxQFVTMyvzfDS1zc2a_1OcB8Jmne3HMDkwPalWXI6l0xOOiMX2ni8vCB1-tfyDJf0YQ1',
    }
    payloadData = {
        "FilterText": "",
        "categoryCode": "{}".format(id),
        "maxResultCount": 20,
        "skipCount": 0,
        "tenantId": "11",
    }
    timeOut = 25
    dumpJsonData = json.dumps(payloadData)
    sesion = requests.session()
    res = sesion.post(url=start_url, headers=headers, data=dumpJsonData, timeout=timeOut)
    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        html = res.text
        if html:
            html = json.loads(html)
            data = html["result"]
            total = int(data["totalCount"])
            if total / 20 == int(total / 20):
                page_all = int(total/20)
            else:
                page_all = int(total/20) + 1
            return page_all


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='panel-body'][string-length()>30]")
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
    div = soup.find('div', class_="panel-body")
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


data = [
    ["gcjs_zhaobiao_gg", "http://www.jnggzyjy.gov.cn/QuFu/Bulletins?CategoryCode=503000",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_old_gg", "http://www.jnggzyjy.gov.cn/QuFu/Bulletins?CategoryCode=001001",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg", "http://www.jnggzyjy.gov.cn/QuFu/Bulletins?CategoryCode=511001",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_old_gg", "http://www.jnggzyjy.gov.cn/QuFu/Bulletins?CategoryCode=001002",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg", "http://www.jnggzyjy.gov.cn/QuFu/Bulletins?CategoryCode=513001",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_liubiao_gg", "http://www.jnggzyjy.gov.cn/QuFu/Bulletins?CategoryCode=517001",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_jingzheng_gg", "http://www.jnggzyjy.gov.cn/QuFu/Bulletins?CategoryCode=002901",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'竞争'}), f2],

    ["zfcg_biangeng_jingzheng_gg", "http://www.jnggzyjy.gov.cn/QuFu/Bulletins?CategoryCode=002904",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'竞争'}), f2],

    ["zfcg_zhongbiao_jingzheng_gg", "http://www.jnggzyjy.gov.cn/QuFu/Bulletins?CategoryCode=002902",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'竞争'}), f2],

    ["zfcg_zhongbiao_old_gg", "http://www.jnggzyjy.gov.cn/QuFu/Bulletins?CategoryCode=002002",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="山东省曲阜市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shandong","qufu"])



