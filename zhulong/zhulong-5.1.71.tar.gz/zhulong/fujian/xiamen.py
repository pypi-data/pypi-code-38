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
from zhulong.util.fake_useragent import UserAgent
import sys
import time
import json
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs


_name_="xiamen"



def f1(driver, num):
    url = driver.current_url
    if "getMongoGovPurchaseNoticePage.do/" in url:
        payloadData = payload_Data(url, num)
        url = url.rsplit('/', maxsplit=1)[0]
    else:
        payloadData = payload_Data(url, num)
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        # 'Cookie': cookiestr,
        'User-Agent': user_agent,
        'Content-Type': 'application/json',
        'Host': 'zyjy.xmas.gov.cn',
    }
    sesion = requests.session()
    res = sesion.post(url=url, headers=headers, data=json.dumps(payloadData))
    # 需要判断是否为登录后的页面
    data_list = []
    time.sleep(2)
    if res.status_code == 200:
        html = res.text
        if html:
            if "getMongoGovPurchaseNoticePage.do" in url:
                html = json.loads(html)
                data = html["data"]
                datalist = data["datalist"]
                for data in datalist:
                    projName = data['projName']
                    publishTime = data['publishTime']
                    link = "http://www.xmzyjy.cn/XmUiForWeb2.0/xmebid/governBid.do?noticeId=" + data['noticeId'] + "&noticeType=" +\
                           "{}".format(noticeType) + "&projCode=" + data['projCode'] + "&projId=" + data['projId']

                    diqu = data['areaCode']
                    xm_num = data['projCode']
                    zb_type = data['organizeForm']
                    info = json.dumps({'diqu':diqu,'xm_num':xm_num,'zb_type':zb_type}, ensure_ascii=False)
                    tmp = [projName, publishTime, link, info]
                    data_list.append(tmp)
            else:
                html = json.loads(html)
                data = html["data"]
                datalist = data["dataList"]
                for data in datalist:
                    if "getConstructInfoPage.do" in url:
                        projName = data['projName']
                        pubDate = data['recordDate']
                        link = "http://www.xmzyjy.cn/XmUiForWeb2.0/xmebid/registerInfo.do?" + "projId=" + data['projId'] + "&dataFrom=" + str(data['dataFrom'])
                        bj_num = data['projCode']
                        info = json.dumps({'bj_num':bj_num}, ensure_ascii=False)
                    elif "/getNoticePage.do" in url:
                        projName = data['projName']
                        pubDate = data['SEND_TIM']
                        link = "http://www.xmzyjy.cn/XmUiForWeb2.0/xmebid/agentBid.do?leftIndex=F006" + "&uniqueId=" + data['uniqueId']
                        xm_num = data['tenderProjCode']
                        hy_type = data['tenderProjType']
                        info = json.dumps({'xm_num': xm_num, 'hy_type':hy_type}, ensure_ascii=False)
                    else:
                        leftIndex = ""
                        if "getBltPage.do" in url:
                            leftIndex = "leftIndex=F001"
                        elif "getAnQuestionPage_project.do" in url:
                            leftIndex = "leftIndex=F002"
                        elif "getEvaBulletinPage.do" in url:
                            leftIndex = "leftIndex=F004"
                        elif "getwinBulletinPage_project.do" in url:
                            leftIndex = "leftIndex=F005"
                        projName = data['projName']
                        try:
                            pubDate = data['pubDate']
                        except:
                            pubDate = data['sendTime']

                        xm_num = data['tenderProjCode']
                        hy_type = data['tenderProjType']
                        info = json.dumps({'xm_num': xm_num, 'hy_type': hy_type}, ensure_ascii=False)
                        link = "http://www.xmzyjy.cn/XmUiForWeb2.0/xmebid/agentBid.do?" + leftIndex + "&uniqueId=" + data['uniqueId'] + "&objId=" + data['bid']
                    tmp = [projName, pubDate, link, info]
                    data_list.append(tmp)
    df = pd.DataFrame(data_list)
    return df


def payload_Data(url, num):
    if "getMongoGovPurchaseNoticePage.do/" in url:
        global noticeType
        noticeType = re.findall(r'/(\d+)', url)[0]
        payloadData = {'pageIndex': "{}".format(num), 'pageSize': "10", 'noticeTitle': "", 'regionCode': "", 'tenderType': "D", 'transType': "", 'pubTime': "",
                       'state': "", 'noticeType': "{}".format(noticeType), 'purchaseType': "", 'searchBeginTime': "", 'searchEndTime': ""}
        return payloadData
    elif "getConstructInfoPage.do" in url:
        payloadData = {'pageIndex':"{}".format(num),'pageSize':"10",'classId':0,'centerId':0,'projNo':"",'projName':"",'ownerDeptName':"",'showRange':"",'searchBeginTime':"",'searchEndTime':""}
    elif "getNoticePage.do" in url:
        payloadData = {'pageIndex':"{}".format(num),'pageSize':"10",'centerId':0,'projName':"",'title':"",'showRange':""}
    else:
        payloadData = {'pageIndex': "{}".format(num), 'pageSize': "10", 'projName': "", 'centerId': 0, 'showRange': "",'tenderProjType': "", 'searchBeginTime': "", 'searchEndTime': ""}

    return payloadData


def f2(driver):
    url = driver.current_url
    payloadData = payload_Data(url, 1)
    if "getMongoGovPurchaseNoticePage.do/" in url:
        url = url.rsplit('/', maxsplit=1)[0]
    num = get_pageall(url, payloadData)

    driver.quit()
    return num


def get_pageall(url, payloadData):
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent,
        'Content-Type': 'application/json',
        'Host': 'zyjy.xmas.gov.cn',
        }
    sesion = requests.session()
    res = sesion.post(url=url, headers=headers, data=json.dumps(payloadData))
    # 需要判断是否为登录后的页面
    # datas = []
    # print(res)
    time.sleep(2)
    if res.status_code == 200:
        html = res.text
        # print(html)
        if html:
            if "getMongoGovPurchaseNoticePage.do" in url:
                html = json.loads(html)
                data = html["data"]
                total = int(data["pagecount"])
                if total / 10 == int(total / 10):
                    page_all = int(total / 10)
                else:
                    page_all = int(total / 10) + 1
                return page_all
            else:
                html = json.loads(html)
                data = html["data"]
                total = int(data["totalPage"])
                return total


def f3(driver, url):
    driver.get(url)
    if "/xmebid/governBid.do?" in url:
        locator = (By.XPATH, "//div[@id='tenderNoticeContent'][string-length()>15]")
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
        div = soup.find('div', id="tenderNoticeContent")
        return div
    elif "/xmebid/registerInfo.do?" in url:
        locator = (By.XPATH, "//table[@class='hasBorder'][string-length()>15]")
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
        div = soup.find('div', style="margin: 30px 30px 5px 30px;")
        return div
    else:
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
        return div


data = [
    ["gcjs_yucai_gg",
     "http://www.xmzyjy.cn/XmUiForWeb2.0/construct/getConstructInfoPage.do",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhaobiao_gg",
     "http://www.xmzyjy.cn/XmUiForWeb2.0/project/getBltPage.do",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_biangeng_gg",
     "http://www.xmzyjy.cn/XmUiForWeb2.0/project/getAnQuestionPage_project.do",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.xmzyjy.cn/XmUiForWeb2.0/project/getEvaBulletinPage.do",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiao_gg",
     "http://www.xmzyjy.cn/XmUiForWeb2.0/project/getwinBulletinPage_project.do",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_yucai_gg",
     "http://www.xmzyjy.cn/XmUiForWeb2.0/project/getNoticePage.do",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://www.xmzyjy.cn/XmUiForWeb2.0/govermentPurchase/getMongoGovPurchaseNoticePage.do/1",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhongbiao_gg",
     "http://www.xmzyjy.cn/XmUiForWeb2.0/govermentPurchase/getMongoGovPurchaseNoticePage.do/2",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_biangeng_gg",
     "http://www.xmzyjy.cn/XmUiForWeb2.0/govermentPurchase/getMongoGovPurchaseNoticePage.do/4",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="福建省厦门市",**args)
    est_html(conp,f=f3,**args)

# 网址更新
if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","fujian","xiamen"])


