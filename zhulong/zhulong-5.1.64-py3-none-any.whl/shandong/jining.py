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
from zhulong.util.etl import est_meta, est_html, gg_existed, add_info

from fake_useragent import UserAgent


_name_="jining"


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
        'User-Agent': user_agent,
        'Content-Type': 'application/json',
        # 'Cookie': 'Abp.Localization.CultureName=zh-CN; UM_distinctid=166bd5a0a591df-06018582a40a3b-68101b7d-1fa400-166bd5a0a5ac63; ASP.NET_SessionId=rnp3pfk0em1sm3pq5mbzmfxo; __RequestVerificationToken=ScDJhFUQHal-xpcDsZZauTKRLdbSRuTF42lP5MQyzAzFfjahmqwGSQW310biEwNoF8sS82aB8tXASg_feKHK0hWo21CkiZrW4JufL88WVCY1; CNZZDATA1273473557=292458821-1540772995-%7C1540806026; Public-XSRF-TOKEN=pXeTT4CHYm4zShxYJjvYzVyUalwAgwUQRS7rxjKackrhszOSUaKgpKS4ZsGxkiAjDjCOTdoyNcOIy93ju8Zq5z0DQUEGCXmQtMM5Z_sSKFQ1',
        'Host':'www.jnggzyjy.gov.cn',
        'Public-X-XSRF-TOKEN': 'pXeTT4CHYm4zShxYJjvYzVyUalwAgwUQRS7rxjKackrhszOSUaKgpKS4ZsGxkiAjDjCOTdoyNcOIy93ju8Zq5z0DQUEGCXmQtMM5Z_sSKFQ1',
    }
    payloadData = {
        "FilterText": "",
        "categoryCode": "{}".format(id),
        "maxResultCount": 20,
        "skipCount": (num - 1) * 20,
        "tenantId": "3",
    }
    # 下载超时
    timeOut = 25
    dumpJsonData = json.dumps(payloadData)
    sesion = requests.session()
    res = sesion.post(url=start_url, headers=headers, data=dumpJsonData,timeout=timeOut)
    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        html = res.text
        # print(html)
        datas = []
        if html:
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
        'User-Agent': user_agent,
        'Content-Type': 'application/json',
        # 'Cookie': 'Abp.Localization.CultureName=zh-CN; UM_distinctid=166bd5a0a591df-06018582a40a3b-68101b7d-1fa400-166bd5a0a5ac63; ASP.NET_SessionId=rnp3pfk0em1sm3pq5mbzmfxo; __RequestVerificationToken=ScDJhFUQHal-xpcDsZZauTKRLdbSRuTF42lP5MQyzAzFfjahmqwGSQW310biEwNoF8sS82aB8tXASg_feKHK0hWo21CkiZrW4JufL88WVCY1; CNZZDATA1273473557=292458821-1540772995-%7C1540806026; Public-XSRF-TOKEN=pXeTT4CHYm4zShxYJjvYzVyUalwAgwUQRS7rxjKackrhszOSUaKgpKS4ZsGxkiAjDjCOTdoyNcOIy93ju8Zq5z0DQUEGCXmQtMM5Z_sSKFQ1',
        'Host':'www.jnggzyjy.gov.cn',
        'Public-X-XSRF-TOKEN': 'pXeTT4CHYm4zShxYJjvYzVyUalwAgwUQRS7rxjKackrhszOSUaKgpKS4ZsGxkiAjDjCOTdoyNcOIy93ju8Zq5z0DQUEGCXmQtMM5Z_sSKFQ1',
    }
    payloadData = {
        "FilterText": "",
        "categoryCode": "{}".format(id),
        "maxResultCount": 20,
        "skipCount": 0,
        "tenantId": "3",
    }
    # 下载超时
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
            if total/20 == int(total/20):
                page_all = int(total/20)
            else:
                page_all = int(total/20) + 1
            return page_all


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='panel-body'][string-length()>15]")
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
    div = soup.find('div', class_="panel-body")
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


data = [
    ["gcjs_zhaobiao_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=503000",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_old_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=001001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_biangeng_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=503002",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_bian_da_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=504002",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_zhongbiaohx_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=511001",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_old_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=001002",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_zhongbiao_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=513001",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_liubiao_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=517001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhaobiao_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=551001",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_jingzheng_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=002901",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'竞争'}), f2],

    ["zfcg_zhaobiao_old_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=00200101",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=552001",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_jingzheng_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=002904",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'竞争'}), f2],

    ["zfcg_biangeng_old_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=002004",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=553001",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_jingzheng_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=002902",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'竞争'}), f2],

    ["zfcg_zhongbiao_old_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=002002",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["yiliao_zhaobiao_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=551002",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["yiliao_zhaobiao_old_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=007001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["yiliao_biangeng_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=552002",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["yiliao_zhongbiao_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=553002",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["yiliao_zhongbiao_old_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=007002",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["qsy_zhaobiao_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=551003",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_zhaobiao_old_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=005001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["qsy_biangeng_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=552003",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["qsy_zhongbiao_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=553003",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_zhongbiao_old_gg", "http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=005002",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]



def work(conp,**args):
    est_meta(conp,data=data,diqu="山东省济宁市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.4.175","shandong","jining"])



    # driver=webdriver.Chrome()
    # url="http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=001001"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    # driver = webdriver.Chrome()
    # url ="http://www.jnggzyjy.gov.cn/JiNing/Bulletins?CategoryCode=001001"
    # driver.get(url)
    # for i in range(3, 6):
    #     df=f1(driver, i)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)