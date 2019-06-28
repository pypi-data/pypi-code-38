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
from collections import OrderedDict

import sys
import time

import json
from zhulong.util.etl import add_info, est_meta, est_html, est_tbs, gg_existed

_name_="nanan"

from zhulong.util.fake_useragent import UserAgent


def f1(driver, num):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s'% proxy}
    except:
        proxies = ''
    url = driver.current_url
    ua = UserAgent()
    user_agent = ua.random
    payloadData,noticeType = payload_Data(url, num)
    start_url = url.rsplit('/', maxsplit=1)[0]
    headers = {
        'User-Agent': user_agent,
        'Content-Type': 'application/json',
        'Host': 'www.nazbcg.gov.cn',
    }
    if proxies:
        res = requests.post(url=start_url, headers=headers, data=json.dumps(payloadData), proxies=proxies)
    else:
        res = requests.post(url=start_url, headers=headers, data=json.dumps(payloadData))
    # 需要判断是否为登录后的页面
    data_list = []
    if res.status_code != 200:
        raise ConnectionError
    else:
        html = res.text
        if html:
            if "getTenderInfoPage.do" in url:
                html = json.loads(html)
                data = html["data"]
                datalist = data["datalist"]
                for data in datalist:
                    projName = data['noticeTitle']
                    publishTime = data['sendTime']
                    try:
                        proj_id = data['proj_id']
                    except:
                        proj_id = ""
                    try:
                        pre_evaId = data['pre_evaId']
                    except:
                        pre_evaId = ""
                    try:
                        evaId = data['evaId']
                    except:
                        evaId = ""
                    try:
                        signUpType = data['signUpType']
                    except:
                        signUpType = ""
                    link = "http://120.33.41.196/hyweb/naebid/bidDetails.do?flag=1&noticeType=" + "{}".format(noticeType) +"&tenderProjCode=" + data['tenderProjCode'] + "&tenderProjId=" +\
                        data['tenderProjId'] + "&proj_id=" + proj_id +"&pre_evaId=" + pre_evaId+ "&evaId=" + evaId + "&signUpType=" + signUpType
                    tmp = [projName, publishTime, link]
                    data_list.append(tmp)
            elif "getMongoGovPurchaseNoticePage.do/z" in url:
                html = json.loads(html)
                data = html["data"]
                datalist = data["datalist"]
                for data in datalist:
                    projName = data['noticeTitle']
                    publishTime = data['publishTime']
                    link = "http://120.33.41.196/hyweb/commons/simpleBidDetails.do?handle=1&projId=" + data['projId'] + "&noticeType=" + "{}".format(noticeType)
                    tmp = [projName, publishTime, link]
                    data_list.append(tmp)
            elif "getMongoGovPurchaseNoticePage.do/g" in url:
                if int(noticeType) != 6:
                    html = json.loads(html)
                    data = html["data"]
                    datalist = data["datalist"]
                    for data in datalist:
                        projName = data['noticeTitle']
                        publishTime = data['publishTime']
                        try:
                            # isCatch = data['isCatch']
                            link ="http://120.33.41.196/hyweb/commons/simpleBidDetails.do?handle="+data['isCatch']+ "&projId=" + data['projId'] + "&noticeType=" + "{}".format(noticeType)
                        except:
                            link = "http://120.33.41.196/hyweb/commons/mongoGovBid.do?projId=" + data['projId'] + "&flag=2&noticeType=" + "{}".format(noticeType)
                        tmp = [projName, publishTime, link]
                        data_list.append(tmp)
                else:
                    html = json.loads(html)
                    data = html["data"]
                    datalist = data["datalist"]
                    for data in datalist:
                        projName = data['noticeTitle']
                        publishTime = data['publishTime']
                        link = "http://120.33.41.196/hyweb/commons/simpleBidDetails.do?handle=4&projId=" + data['projId'] + "&noticeType=6"
                        tmp = [projName, publishTime, link]
                        data_list.append(tmp)

            else:
                html = json.loads(html)
                data = html["data"]
                datalist = data["datalist"]
                for data in datalist:
                    projName = data['title']
                    publishTime = data['publishTime']
                    link = "http://120.33.41.196/hyweb/naebid/otherBid.do?srcNoticeId=" + data['noticeId'] + "&noticeType=" + "{}".format(noticeType)
                    tmp = [projName, publishTime, link]
                    data_list.append(tmp)


    df = pd.DataFrame(data_list)
    df['info'] = None
    return df


def payload_Data(url, num):

    if "/getTenderInfoPage.do/j=" in url:

        noticeType = re.findall(r'/j=(\d+)', url)[0]

        payloadData = {'pageIndex':"{}".format(num),'pageSize':"10",'noticeTitle':"",'regionCode':"350500",'tenderType':"A",'transType' :"",'pubTime' :"",'state' :"",'noticeType' :"{}".format(noticeType),'tradeCode':"1"}
        return payloadData,noticeType

    elif "/getTenderInfoPage.do/x=" in url:

        noticeType = re.findall(r'/x=(\d+)', url)[0]

        payloadData = {'pageIndex':"{}".format(num),'pageSize':"10",'noticeTitle':"",'regionCode':"350500",'tenderType':"A",'transType' :"",'pubTime' :"",'state' :"",'noticeType' :"{}".format(noticeType),'tradeCode':"2"}
        return payloadData,noticeType

    elif "/getMongoGovPurchaseNoticePage.do/z=" in url:

        noticeType = re.findall(r'/z=(\d+)', url)[0]

        payloadData = {'pageIndex':"{}".format(num),'pageSize':"10",'noticeTitle':"",'regionCode':"350500",'tenderType':"D",'transType' :"",'pubTime' :"",'state' :"",'noticeType' :"{}".format(noticeType)}
        return payloadData,noticeType

    elif "/getMongoGovPurchaseNoticePage.do/g=" in url:

        noticeType = re.findall(r'/g=(\d+)', url)[0]

        payloadData = {'pageIndex':"{}".format(num),'pageSize':"10",'noticeTitle':"",'regionCode':"350500",'tenderType':"DD",'transType' :"",'pubTime' :"",'state' :"",'noticeType' :"{}".format(noticeType)}
        return payloadData,noticeType

    elif "/getOtherTradeNoticePage.do/q=" in url:

        noticeType = re.findall(r'/q=(\d+)', url)[0]

        payloadData = {'pageIndex':"{}".format(num),'pageSize':"10",'noticeTitle':"",'regionCode':"350500",'tenderType':"Z",'transType' :"",'pubTime' :"",'state' :"",'noticeType' :"{}".format(noticeType)}
        return payloadData,noticeType



def f2(driver):
    url = driver.current_url
    payloadData,noticeType = payload_Data(url, 1)
    url = url.rsplit('/', maxsplit=1)[0]
    num = get_pageall(url, payloadData)
    driver.quit()
    return num


def get_pageall(url, payloadData):
    ua = UserAgent()
    user_agent = ua.random
    headers = {
        'User-Agent': user_agent,
        'Content-Type': 'application/json',
        'Host': 'www.nazbcg.gov.cn',
        }
    sesion = requests.session()
    res = sesion.post(url=url, headers=headers, data=json.dumps(payloadData))
    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        html = res.text
        if html:
            html = json.loads(html)
            data = html["data"]
            total = int(data["pagecount"])
            if total / 10 == int(total / 10):
                page_all = int(total / 10)
            else:
                page_all = int(total / 10) + 1
            return page_all


def f3(driver, url):
    driver.get(url)
    if "naebid/otherBid.do?srcNoticeId=" in url:
        locator = (By.XPATH, "//div[@id='main'][string-length()>30]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
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
        div = soup.find('div', id="main")
        return div
    elif "commons/simpleBidDetails.do" in url:
        locator = (By.XPATH, "//div[@id='main'][string-length()>30]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
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
        div = soup.find('div', id="main")
        return div
    elif "/naebid/bidDetails.do" in url:
        locator = (By.XPATH, "//div[@id='main'][string-length()>30]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        flag = re.findall(r'noticeType=(\d+?)', url)[0]
        fl1 = OrderedDict([('1', '招标公告'), ('2', '变更公告'), ('3', '中标候选人公示'),
                           ('4', '中标公示'), ('8', '资格预审'), ('7', '异常公告')])
        if int(flag) == 8:
            flag='1'
        locator = (By.XPATH, "//div[@id='main'][string-length()>30]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH,"//span[@id='noticeTitleName'][contains(string(), '%s')] | //span[@id='noticeTitle'][contains(string(),%s)]" % (fl1[flag], fl1[flag]))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        time.sleep(random.uniform(1, 3))
        before = len(driver.page_source)
        time.sleep(0.5)
        after = len(driver.page_source)
        i = 0
        while before != after:
            before = len(driver.page_source)
            time.sleep(0.5)
            after = len(driver.page_source)
            i += 1
            if i > 5: break
        page = driver.page_source
        if 'class="emptyNotice"' in page:
            return '暂无发布内容'
        elif 'id="iframepage"' in page:
            div = get_iframe_data(driver)
            return div
        else:
            soup = BeautifulSoup(page, 'html.parser')
            div = soup.find('div', class_="details_content")
            return div

    else:
        locator = (By.XPATH, "//div[@id='main'][string-length()>30]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        fl2 = OrderedDict([('1', '采购/资审公告'), ('6', '预采公告'), ('2', '中标公告'),
                           ('4', '更正事项'), ('7', '招标终止公告')])
        flag = re.findall(r'noticeType=(\d+?)', url)[-1]
        locator = (By.XPATH, "//div[@id='main'][string-length()>15]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, "//span[@id='noticeTitleName'][contains(string(), '%s')] | //span[@id='noticeTitle'][contains(string(), '%s')]" % (fl2[flag], fl2[flag]))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        time.sleep(random.uniform(1, 2))
        before = len(driver.page_source)
        time.sleep(0.5)
        after = len(driver.page_source)
        i = 0
        while before != after:
            before = len(driver.page_source)
            time.sleep(0.5)
            after = len(driver.page_source)
            i += 1
            if i > 5: break
        page = driver.page_source
        if 'class="emptyNotice"' in page:
            return '暂无发布内容'
        elif 'id="iframepage"' in page:
            div = get_iframe_data(driver)
            return div
        else:
            soup = BeautifulSoup(page, 'html.parser')
            div = soup.find('div', class_="details_content")
            return div


def get_iframe_data(driver, ):
    locator = (By.XPATH, "//iframe[@id='iframepage']")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    driver.switch_to_frame('iframepage')

    locator = (By.XPATH, "//embed[@id='plugin'] | (//div[@class='textLayer'])[last()][string-length()>10]")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, '//input[@id="pageNumber"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    tnum = driver.find_element_by_xpath('//span[@id="numPages"]').text.strip()
    tnum = int(re.findall(r'(\d+)', tnum)[0])
    if tnum != 1:
        for _ in range(tnum-1):
            locator = (By.XPATH, "//button[@id='next']")
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).click()

    locator = (By.XPATH, '//span[@id="numPages"]')
    tnum = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text.strip()
    tnum = int(re.findall(r'(\d+)', tnum)[0])
    try:
        locator = (By.XPATH, "//embed[@id='plugin'] | (//div[@class='textLayer'])[{}][string-length()>15]".format(tnum))
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    except:
        locator = (By.XPATH, "//embed[@id='plugin'] | (//div[@class='textLayer'])[{}][string-length()>15]".format(tnum-1))
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
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
    divs = soup.find_all('div', class_="textLayer")
    div = ''
    for di in divs:div+=str(di)
    if (div == None) or (div == ''):div = soup.find('embed', id="plugin")['src']
    driver.switch_to_default_content()
    return div



data = [
    ["gcjs_zhaobiao_gg",
     "http://120.33.41.196/hyweb/transInfo/getTenderInfoPage.do/j=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_biangeng_gg",
     "http://120.33.41.196/hyweb/transInfo/getTenderInfoPage.do/j=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://120.33.41.196/hyweb/transInfo/getTenderInfoPage.do/j=3",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://120.33.41.196/hyweb/transInfo/getTenderInfoPage.do/j=4",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zgys_gg",
     "http://120.33.41.196/hyweb/transInfo/getTenderInfoPage.do/j=8",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_liubiao_gg",
     "http://120.33.41.196/hyweb/transInfo/getTenderInfoPage.do/j=7",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_xiaoe_gg",
     "http://120.33.41.196/hyweb/transInfo/getTenderInfoPage.do/x=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_biangeng_xiaoe_gg",
     "http://120.33.41.196/hyweb/transInfo/getTenderInfoPage.do/x=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_xiaoe_gg",
     "http://120.33.41.196/hyweb/transInfo/getTenderInfoPage.do/x=3",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_xiaoe_gg",
     "http://120.33.41.196/hyweb/transInfo/getTenderInfoPage.do/x=4",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_liubiao_xiaoe_gg",
     "http://120.33.41.196/hyweb/transInfo/getTenderInfoPage.do/x=7",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://120.33.41.196/hyweb/govPurchase/getMongoGovPurchaseNoticePage.do/z=1",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhongbiao_gg",
     "http://120.33.41.196/hyweb/govPurchase/getMongoGovPurchaseNoticePage.do/z=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://120.33.41.196/hyweb/govPurchase/getMongoGovPurchaseNoticePage.do/z=4",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["qsy_zhaobiao_gg",
     "http://120.33.41.196/hyweb/govPurchase/getMongoGovPurchaseNoticePage.do/g=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_yucai_gg",
     "http://120.33.41.196/hyweb/govPurchase/getMongoGovPurchaseNoticePage.do/g=6",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_gqita_zhong_liu_gg",
     "http://120.33.41.196/hyweb/govPurchase/getMongoGovPurchaseNoticePage.do/g=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_biangeng_gg",
     "http://120.33.41.196/hyweb/govPurchase/getMongoGovPurchaseNoticePage.do/g=4",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_liubiao_gg",
     "http://120.33.41.196/hyweb/govPurchase/getMongoGovPurchaseNoticePage.do/g=7",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhaobiao_gg",
     "http://120.33.41.196/hyweb/otherTrade/getOtherTradeNoticePage.do/q=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_gqita_zhong_liu_gg",
     "http://120.33.41.196/hyweb/otherTrade/getOtherTradeNoticePage.do/q=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="福建省南安市",**args)
    est_html(conp,f=f3,**args)


# 修改日期：2019/6/27
# 网址变更：http://www.nanan.gov.cn/zwgk/ztzl/ggzyjy/
# f3更改
if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","fujian","nanan"],pageloadtimeout=60)

    #
    # for d in data[1:]:
    #     url = d[1]
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #     d1 = f2(driver)
    #     print(d1)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #     d2 = f1(driver, 1)
    #     print(d2.values)
    #     for i in d2[2].tolist():
    #         f = f3(driver, i)
    #         print(f)







