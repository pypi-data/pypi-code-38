import json
import math
import random
import re
import time
from datetime import datetime, timedelta
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
from zhulong.util.etl import est_html, est_meta, add_info
import time
from zhulong.util.fake_useragent import UserAgent
_name_ = 'wuhan'
headless_flag=True

def get_cookies_headers_params():
    global cookies, headers, data_params
    UA = UserAgent()

    chrome_option = webdriver.ChromeOptions()
    if headless_flag:chrome_option.add_argument('--headless')
    chrome_option.add_argument('--no-sandbox')
    chrome_option.add_experimental_option('excludeSwitches', ['enable-automation'])
    d = webdriver.Chrome(chrome_options=chrome_option)
    d.get('http://www.whzbtb.com/V2PRTS/wz/201311080946010001/wzsy/201312261004550001.html')
    # print(d.execute_script("""return navigator.userAgent;"""))
    cookies_list = d.get_cookies()
    cookies1 = ''
    for c in cookies_list:
        cookies1 += (c['name'])
        cookies1 += ('=' + c['value'])
        cookies1 += ';'
    # print('cookies', cookies)
    d.quit()

    headers1 = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': cookies1,
        'Host': 'www.jy.whzbtb.cn',
        'Referer': 'http://www.jy.whzbtb.cn/V2PRTS/TendererNoticeInfoListInit.do',
        'Origin': 'http://www.jy.whzbtb.cn',
        'User-Agent': UA.random,
        'X-Requested-With': 'XMLHttpRequest',
    }

    url = "http://www.jy.whzbtb.cn/V2PRTS/TendererNoticeInfoList.do"
    data_params1 = {
        'page': '1',
        'rows': '20',
    }
    cookies, headers, data_params = cookies1, headers1,data_params1

proxy, headers, data_params,cookies = {},{},{},''


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


# get_ip()


def f1(driver, num):
    if headers == {}:get_cookies_headers_params()
    headers1 = headers.copy()
    headers1['Referer'] = driver.current_url

    data2 = data_params.copy()
    data2['page'] = num
    driver_info = webdriver.DesiredCapabilities.CHROME
    url_temp = driver.current_url.split('ListInit')[0]

    try:
        if "--proxy" in driver_info['goog:chromeOptions']['args'][0]:

            proxy_ip = driver_info['goog:chromeOptions']['args'][0].split('=')[1]
            proxies = {proxy_ip[0]: proxy_ip[1]}
            response = json.loads(
                requests.post(driver.current_url.replace('Init', ''), proxies=proxies, headers=headers1, data=data2,
                              timeout=40).content.decode())
        else:
            response = json.loads(requests.post(driver.current_url.replace('Init', ''), headers=headers1, data=data2,
                                                timeout=40).content.decode())
    except:
        try:
            response = json.loads(
                requests.post(driver.current_url.replace('Init', ''), headers=headers1, data=data2, proxies=proxy,
                              timeout=40).content.decode())
        except:
            get_ip()
            response = json.loads(
                requests.post(driver.current_url.replace('Init', ''), headers=headers1, data=data2, proxies=proxy,
                              timeout=40).content.decode())
    data_temp = []
    content_list = response.get("rows")
    # print(content_list)
    for content in content_list:
        if 'Tenderer' in driver.current_url:
            name = content.get("tenderPrjName")
            href = url_temp + "Detail.do?id=" + content.get("id")
            ggstart_time = content.get("noticeStartDate")
            noticeStateName = content.get("noticeStateName")
            platformDataSourceName = content.get("platformDataSourceName")
            totalInvestment = content.get("totalInvestment")
            noticeEndDate = content.get("noticeEndDate")
            prjbuildCorpName = content.get("prjbuildCorpName")
            registrationId = content.get("registrationId")

            info = json.dumps({
                'noticeState': noticeStateName,
                'dataFrom': platformDataSourceName,
                'totalMoney': totalInvestment,
                'zhaoBiaoRen': prjbuildCorpName,
                'noticeEndDate': noticeEndDate,
                'registrationId': registrationId,
            }, ensure_ascii=False)
        elif 'Amend' in driver.current_url:
            name = content.get("amendBulletinName")
            href = url_temp + "Detail.do?id=" + content.get("id")
            ggstart_time = content.get("amendBulletinIssueTime")
            originalBulletinCode = content.get("originalBulletinCode")
            info = json.dumps({
                'originalBulletinCode': originalBulletinCode,

            }, ensure_ascii=False)

        elif 'WinBid' in driver.current_url:
            name = content.get("prjName")
            href = url_temp + "Detail.do?id=" + content.get("id")
            ggstart_time = content.get("insertDate")
            zhongbiaoren = content.get("bidderName")
            zhongbiaojiage = content.get("winBidPrice")
            zhonbiao_code = content.get("publicityNumber")
            tenderCorp = content.get("tenderCorp")
            agencyCorp = content.get("agencyCorp")
            info = json.dumps({
                'agencyCorp': agencyCorp,
                'tenderCorp': tenderCorp,
                'zhonbiao_code': zhonbiao_code,
                'zhongbiaojiage': zhongbiaojiage,
                'zhongbiaoren': zhongbiaoren,
            }, ensure_ascii=False)

        elif 'Abandon' in driver.current_url:
            name = content.get("prjName")
            href = url_temp + "Detail.do?abandonNum=" + content.get("id")
            ggstart_time = content.get("abandonStartDate")
            basicInfoName = content.get("basicInfoName")
            state = content.get("state")

            info = json.dumps({
                'state': state,
                'basicInfoName': basicInfoName,
            }, ensure_ascii=False)

        elif 'PrequalificationPublicity' in driver.current_url:

            name = content.get("prjName")
            href = url_temp + "Detail.do?id=" + content.get("id")
            ggstart_time = content.get("prequalificationStartDate")
            prequalificationCorpName = content.get("prequalificationCorpName")
            announcementId = content.get("announcementId")
            prequalificationEndDate = content.get("prequalificationEndDate")
            registrationId = content.get("registrationId")

            info = json.dumps({
                '资格预审单位': prequalificationCorpName,
                '招标公告 ': announcementId,
                '招标登记编号': registrationId,
                '预审公示结束时间': prequalificationEndDate,
            }, ensure_ascii=False)
        elif 'Winning' in driver.current_url:

            name = content.get("prjName")
            href = url_temp + "Detail.do?id=" + content.get("id")
            ggstart_time = content.get("publicityEndDate")

            tenderContent = content.get("tenderContent")
            tenderTypeName = content.get("tenderTypeName")
            corpName = content.get("corpName")
            winningPrice = content.get("winningPrice")
            publicityEndDate = content.get("publicityEndDate")

            info = json.dumps({
                'publicityEndDate': publicityEndDate,
                'corpName ': corpName,
                'tenderContent ': tenderContent,
                'tenderTypeName': tenderTypeName,
                'winningPrice': str(winningPrice) + ' 万元',
            }, ensure_ascii=False)

        elif 'Control' in driver.current_url:

            name = content.get("tenderPrjName")
            href = url_temp + "Detail.do?id=" + content.get("id")
            ggstart_time = content.get("publicityBeginDate")

            tenderCorpName = content.get("tenderCorpName")
            tendererNoticeId = content.get("tendererNoticeId")
            publicityEndDate = content.get("publicityEndDate")

            info = json.dumps({
                'publicityEndDate': publicityEndDate,
                'tendererNoticeId ': tendererNoticeId,
                'tenderCorpName ': tenderCorpName,
            }, ensure_ascii=False)

        elif 'TenderAbnormal' in driver.current_url:

            name = content.get("prjName")
            bidSectionCode = content.get("bidSectionCode")
            href = url_temp + "Detail.do?id=" + content.get("id") + '&bidSectionCode=' + bidSectionCode
            ggstart_time = 'None'

            corpName = content.get("corpName")
            agencyCorpName = content.get("agencyCorpName")
            regulatorsName = content.get("regulatorsName")
            noticeStateName = content.get("noticeStateName")

            info = json.dumps({
                'corpName': corpName,
                'agencyCorpName ': agencyCorpName,
                'regulatorsName ': regulatorsName,
                'noticeStateName ': noticeStateName,
            }, ensure_ascii=False)
        elif 'PrequalificationClarify' in driver.current_url:
            ggstart_time = 'None'
            name = content.get("tenderPrjName")
            tenderClassNumName = content.get("tenderClassNumName")
            href = url_temp + "Detail.do?id=" + content.get("id")
            tenderTypeNumName = content.get("tenderTypeNumName")
            prjbuildCorpName = content.get("prjbuildCorpName")
            info = json.dumps({
                'tenderClassNumName': tenderClassNumName,
                'tenderTypeNumName ': tenderTypeNumName,
                'prjbuildCorpName ': prjbuildCorpName,
            }, ensure_ascii=False)
        elif 'CorpInfo' in driver.current_url:

            name = content.get("corpName")
            economicNumName = content.get("economicNumName")
            href = url_temp + "Detail.do?id=" + content.get("id")
            corpBirthDate = content.get("corpBirthDate")
            ggstart_time = 'None'
            regPrin = content.get("regPrin")
            info = json.dumps({
                'economicNumName': economicNumName,
                'corpBirthDate ': corpBirthDate,
                'regPrin ': str(regPrin) + ' 万元',
            }, ensure_ascii=False)
        temp = [name, ggstart_time, href, info]
        data_temp.append(temp)
    df = pd.DataFrame(data=data_temp)

    return df


def f2(driver):
    if data_params == {} : get_cookies_headers_params()
    data1 = data_params.copy()

    headers['Referer'] = driver.current_url

    driver_info = webdriver.DesiredCapabilities.CHROME
    try:
        if "--proxy" in driver_info['goog:chromeOptions']['args'][0]:

            proxy_ip = driver_info['goog:chromeOptions']['args'][0].split('=')[1]
            proxies = {proxy_ip[0]: proxy_ip[1]}

            response = json.loads(
                requests.post(driver.current_url.replace('Init', ''), proxies=proxies, headers=headers, data=data1,
                              timeout=40).content.decode())
        else:
            response = json.loads(requests.post(driver.current_url.replace('Init', ''), headers=headers, data=data1,
                                                timeout=40).content.decode())
    except:
        response = json.loads(
            requests.post(driver.current_url.replace('Init', ''), headers=headers, data=data1, proxies=proxy,
                          timeout=40).content.decode())
    total_page = math.ceil(int(response.get('total')) / 20)
    # print(response)
    driver.quit()
    return int(total_page)


def f3(driver, url):
    UA = UserAgent()
    headers3 = {
        'Cookie': 'JSESSIONID=0AD8CE34B65F3090AA7CA6EF61E8A18E.tomcat6_system_portal; safedog-flow-item=; Hm_lvt_584478b66df9baddcb4e23391c58fdfb=1556106562,1556123479,1556155457,1556161474; Hm_lpvt_584478b66df9baddcb4e23391c58fdfb=1556176718; sequence="3WJo44XI3YAVt6SkwfCtpUatXE5kgzGWveCKIvxo0+U="',
        'User-Agent':UA.random,
    }
    headers3['Cookie'] = cookies
    driver_info = webdriver.DesiredCapabilities.CHROME

    time.sleep(random.randint(3, 6))

    try:
        if "--proxy" in driver_info['goog:chromeOptions']['args'][0]:

            proxy_ip = driver_info['goog:chromeOptions']['args'][0].split('=')[1]
            proxies = {proxy_ip[0]: proxy_ip[1]}
            page = requests.get(url, proxies=proxies, headers=headers3, timeout=40).content.decode()
        else:
            page = requests.get(url, headers=headers3, timeout=40).content.decode()
    except:
        try:
            page = requests.get(url, headers=headers3, proxies=proxy, timeout=40).content.decode()
        except:
            get_ip()
            page = requests.get(url, headers=headers3, proxies=proxy, timeout=40).content.decode()

    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_='trading_publicly_fr fr')
    if not div: raise Exception('Div is None')

    return div



data = [
    ["gcjs_gqita_zhao_zgys_gg",
     "http://www.jy.whzbtb.cn/V2PRTS/TendererNoticeInfoListInit.do",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_biangeng_gg",
     "http://www.jy.whzbtb.cn/V2PRTS/AmendBulletinInfoListInit.do",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://www.jy.whzbtb.cn/V2PRTS/WinBidBulletinInfoListInit.do",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_fangqi_gg",
     "http://www.jy.whzbtb.cn/V2PRTS/AbandonNoticeInfoListInit.do",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'Tag': '放弃中标'}), f2],

    ["gcjs_zgysjg_gg",
     "http://www.jy.whzbtb.cn/V2PRTS/PrequalificationPublicityInfoListInit.do",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    #
    ["gcjs_zhongbiaohx_gg",
     "http://www.jy.whzbtb.cn/V2PRTS/WinningPublicityInfoListInit.do",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_kongzhijia_gg",
     "http://www.jy.whzbtb.cn/V2PRTS/ControlPriceListInit.do",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_liubiao_gg",
     "http://www.jy.whzbtb.cn/V2PRTS/TenderAbnormalReportInfoListInit.do",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'Tag': '招标异常报告'}), f2],

    ["gcjs_zgys_gg",
     "http://www.jy.whzbtb.cn/V2PRTS/PrequalificationClarifyInfoListInit.do",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'Tag': '资格预审澄清'}), f2],

    ["gcjs_gqita_qyxx_gg",
     "http://www.jy.whzbtb.cn/V2PRTS/CorpInfoListInit.do",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'Tag': '企业信息'}), f2],

]


def work(conp, **args):
    global headless_flag
    '''
    武汉本代码只能在windows平台运行。
    linux会被检测为移动端访问。暂未解决。
    '''
    if 'headless' in  args.keys():
        headless_flag = args.get('headless')
    est_meta(conp, data=data, diqu="湖北省武汉市", **args)
    est_html(conp, f=f3, **args)



if __name__ == '__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "anbang", "hubei_wuhan"]
    work(conp,headless=False)
    # driver.get(url)
    # print(f3(driver, 'http://www.jy.whzbtb.cn/V2PRTS/PrequalificationPublicityInfoDetail.do?id=201802011155591843'))
    # driver.quit()
