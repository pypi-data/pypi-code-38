
import pandas as pd
import re

import requests
from zhulong.util.fake_useragent import UserAgent
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
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs


_name_="wuyishan"



start_url, pay=None, None


def zfcg_data(driver, num):
    url = driver.current_url
    locator = (By.XPATH, "//table[@class='table table-hover dataTables-example']/tbody/tr[1]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//button[@class='active']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        cnum = int(st)
    except:
        cnum = 1
    try:
        notice_type = re.findall(r'notice_type=(.*)&', url)[0]
    except:
        notice_type = re.findall(r'notice_type=(.*)', url)[0]

    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@class='table table-hover dataTables-example']/tbody/tr[1]/td/a").get_attribute('href')[-30:]
        driver.execute_script("javascript:location.href='?page={0}&notice_type={1}'".format(num, notice_type))
        # driver.execute_script("javascript:location.href='?page=6&notice_type=7dc00df822464bedbf9e59d02702b714'")
        try:
            locator = (By.XPATH,
                       "//table[@class='table table-hover dataTables-example']/tbody/tr[1]/td/a[not(contains(@href,'%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            driver.refresh()
            locator = (By.XPATH,
                       "//table[@class='table table-hover dataTables-example']/tbody/tr[1]/td/a[not(contains(@href,'%s'))]" % val)
            WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", class_="table table-hover dataTables-example")
    tbody = table.find('tbody')
    trs = tbody.find_all("tr", class_="gradeX")
    data = []
    for tr in trs:
        a = tr.find('a')
        try:
            title = a["title"].strip()
        except:
            title = a.text.strip()
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = "http://np.fjzfcg.gov.cn:8090" + link.strip()
        td = tr.find_all("td")[4].text.strip()
        diqu = tr.find_all("td")[0].text.strip()
        cgfs = tr.find_all("td")[1].text.strip()
        cgdw = tr.find_all("td")[2].text.strip()
        dd = {'diqu': diqu, 'cgfs': cgfs, 'cgdw': cgdw}
        info = json.dumps(dd, ensure_ascii=False)
        tmp = [title, td, href, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f1(driver, num):
    url = driver.current_url
    if "http://np.fjzfcg.gov.cn" in url:
        df = zfcg_data(driver, num)
        return df
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent,
    }
    payloadData,noticeType = get_payloadData(pay, num)
    sesion = requests.session()
    res = sesion.post(url=start_url, headers=headers, data=json.dumps(payloadData))
    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        html = res.text
        if html:
            html = json.loads(html)
            datalist = html["data"]['datalist']
            data = []
            for tr in datalist:
                if 'gcjs' in pay:
                    try:
                        tenderProjId = tr['tenderProjId']
                    except:
                        tenderProjId = ''
                    try:
                        proj_id = tr['proj_id']
                    except:
                        proj_id = ''
                    try:
                        pre_evaId = tr['pre_evaId']
                    except:
                        pre_evaId = ''
                    try:
                        evaId = tr['evaId']
                    except:
                        evaId = ''
                    try:
                        signUpType = tr['signUpType']
                    except:
                        signUpType = ''
                    try:
                        tenderProjCode = tr['tenderProjCode']
                    except:
                        tenderProjCode = ''
                    link = 'http://www.wysggzy.cn:81/hyweb/wysebid/bidDetails.do?handle=1&tenderProjCode='+tenderProjCode+'&noticeType='+noticeType+'&flag=1&tenderProjId='+tenderProjId+'&proj_id='+proj_id+'&pre_evaId='+pre_evaId+'&evaId='+evaId+'&signUpType='+signUpType
                    title = tr['noticeTitle']
                    try:
                        td = tr['sendTime']
                    except:
                        td = '-'
                    tmp = [title, td, link]
                    data.append(tmp)
            df = pd.DataFrame(data)
            df['info'] = None
            return df


def get_payloadData(pay, num):
    if pay == 'gcjs_zb':
        payloadData = {'pageIndex': num, 'pageSize': 10, 'tradeCode': 'WYSPT', 'noticeTitle': "", 'regionCode': "", 'tenderType': "G",'transType': "", 'pubTime': "", 'state': "", 'noticeType': 1}
        noticeType = '1'
    elif pay == 'gcjs_bg':
        payloadData = {'pageIndex': num, 'pageSize': 10, 'tradeCode': 'WYSPT', 'noticeTitle': "", 'regionCode': "", 'tenderType': "G",'transType': "", 'pubTime': "", 'state': "", 'noticeType': 2}
        noticeType = '2'
    elif pay == 'gcjs_zbhx':
        payloadData = {'pageIndex': num, 'pageSize': 10, 'tradeCode': 'WYSPT', 'noticeTitle': "", 'regionCode': "",'tenderType': "G", 'transType': "", 'pubTime': "", 'state': "", 'noticeType': 3}
        noticeType = '3'
    elif pay == 'gcjs_zhb':
        payloadData = {'pageIndex': num, 'pageSize': 10, 'tradeCode': 'WYSPT', 'noticeTitle': "", 'regionCode': "",'tenderType': "G", 'transType': "", 'pubTime': "", 'state': "", 'noticeType': 4}
        noticeType = '4'
    return payloadData,noticeType





def f2(driver):
    url = driver.current_url
    if "http://np.fjzfcg.gov.cn" in url:
        locator = (By.XPATH, "//button[@class='active']")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        locator = (By.XPATH, "//div[@class='pageGroup']/button[last()]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        try:
            locator = (By.XPATH, "//button[@class='active'][not(contains(string(),'%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            locator = (By.XPATH, "//button[@class='active']")
            st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num = int(st)
        except:
            num = 1
        driver.quit()
        return int(num)

    global start_url,pay
    start_url,pay=None,None
    start_url = url.rsplit('/', maxsplit=1)[0]
    pay = url.rsplit('/', maxsplit=1)[1]
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent,
    }
    payloadData,noticeType = get_payloadData(pay, 1)
    sesion = requests.session()
    res = sesion.post(url=start_url, headers=headers, data=json.dumps(payloadData))
    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        html = res.text
        if html:
            html = json.loads(html)
            total = html["data"]['pagecount']
            if total/10 == int(total/10):
                num_total = int(total/10)
            else:
                num_total = int(total/10) + 1

    driver.quit()
    return int(num_total)




def f3(driver, url):
    driver.get(url)
    if "http://np.fjzfcg.gov.cn" in url:
        locator = (By.XPATH, "//div[@id='print-content'][string-length()>15]")
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
        div = soup.find('div', id="print-content")
        return div

    locator = (By.XPATH, "//div[@class='ggnr_con'][string-length()>15]")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    time.sleep(3)
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


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.wysggzy.cn:81/hyweb/transInfo/getTenderInfoPage.do/gcjs_zb",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_biangeng_gg",
     "http://www.wysggzy.cn:81/hyweb/transInfo/getTenderInfoPage.do/gcjs_bg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.wysggzy.cn:81/hyweb/transInfo/getTenderInfoPage.do/gcjs_zbhx",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://www.wysggzy.cn:81/hyweb/transInfo/getTenderInfoPage.do/gcjs_zhb",
     ["name", "ggstart_time", "href", "info"],f1,f2],
    #
    ["zfcg_zhaobiao_gg",
     "http://np.fjzfcg.gov.cn:8090/350782/noticelist/d03180adb4de41acbb063875889f9af1/?zone_code=&zone_name=&croporgan_name=武夷山市&project_no=&fromtime=&endtime=&gpmethod=&agency_name=&title=&notice_type=463fa57862ea4cc79232158f5ed02d03&purchase_item_name=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://np.fjzfcg.gov.cn:8090/350782/noticelist/d03180adb4de41acbb063875889f9af1/?zone_code=&zone_name=&croporgan_name=武夷山市&project_no=&fromtime=&endtime=&gpmethod=&agency_name=&title=&notice_type=7dc00df822464bedbf9e59d02702b714&purchase_item_name=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://np.fjzfcg.gov.cn:8090/350782/noticelist/d03180adb4de41acbb063875889f9af1/?zone_code=&zone_name=&croporgan_name=武夷山市&project_no=&fromtime=&endtime=&gpmethod=&agency_name=&title=&notice_type=b716da75fe8d4e4387f5a8c72ac2a937&purchase_item_name=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_jieguo_gg",
     "http://np.fjzfcg.gov.cn:8090/350782/noticelist/d03180adb4de41acbb063875889f9af1/?zone_code=&zone_name=&croporgan_name=武夷山市&project_no=&fromtime=&endtime=&gpmethod=&agency_name=&title=&notice_type=d812e46569204c7fbd24cbe9866d0651&purchase_item_name=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_danyilaiyuan_gg",
     "http://np.fjzfcg.gov.cn:8090/350782/noticelist/d03180adb4de41acbb063875889f9af1/?zone_code=&zone_name=&croporgan_name=武夷山市&project_no=&fromtime=&endtime=&gpmethod=&agency_name=&title=&notice_type=255e087cf55a42139a1f1b176b244ebb&purchase_item_name=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"zbfs":"单一来源"}), f2],
]


def work(conp,**args):
    est_meta(conp,data=data,diqu="福建省武夷山市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","fujian","wuyishan"])



