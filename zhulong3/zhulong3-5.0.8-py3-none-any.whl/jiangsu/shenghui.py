import json
import math
import random
import re

import requests
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong3.util.etl import est_html, est_meta, add_info
import time
from urllib.parse import urlparse,parse_qs

_name_ = 'jiangsu_shenghui'

data_param = {
'__EVENTTARGET': 'MoreInfoList1$Pager',
'__EVENTARGUMENT': '2',
'__LASTFOCUS': '',
'__VIEWSTATE': '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',

'__VIEWSTATEGENERATOR': '76D0A3AC',
'__VIEWSTATEENCRYPTED': '',
'__EVENTVALIDATION': '2qn4vwBp3Je41UCOFkmyPMlQuxUu6wcIEenT9Fw5idpelEgrFs3JgfwDgmYWF6MOEuHF2CSKigfDDzka6Fh+RJvbIJD5olYHdNAqpBedwsTmP2l/N8Z3JgLowP2ZMCJvuwdNgWFT43ZVJd0r0bUB8mH1sgR+a9C+AKlU72Yt88Z3HGxZ5P+KLsv1WG44j6Th+ao7Cqkc91JouLOE8bX0SyXAQlHCjY6/HJmvFTjJC5n4UviR3EjqemL1h3b7o90z+JsCmUFa30dTulSyxq28TbYDxJHH0CBp6FVeIg==',
'MoreInfoList1$txtProjectName': '',
'MoreInfoList1$txtBiaoDuanName': '',
'MoreInfoList1$txtBiaoDuanNo': '',
'MoreInfoList1$txtJSDW': '',
'MoreInfoList1$StartDate': '2019-01-01',
'MoreInfoList1$EndDate': '',
'MoreInfoList1$jpdDi': '-1',
'MoreInfoList1$jpdXian': '-1',
}
headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
'Cache-Control': 'max-age=0',
'Connection': 'keep-alive',
'Content-Length': '29217',
'Content-Type': 'application/x-www-form-urlencoded',
'Cookie': 'ASP.NET_SessionId=ay5thse0emrcn4npto44onz5',
'Host': 'www.jszb.com.cn',
'Origin': 'http://www.jszb.com.cn',
'Referer': 'http://www.jszb.com.cn/jszb/YW_info/ZhaoBiaoGG/MoreInfo_ZBGG.aspx?categoryNum=012&a=MoreInfoList1%24Pager',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',}

def f1(driver, num):
    target = parse_qs(driver.current_url).get('target')[0]

    viewstate = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.ID,'__VIEWSTATE'))).get_attribute('value')
    viewstategenerator = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.ID,'__VIEWSTATEGENERATOR'))).get_attribute('value')
    eventvalidation = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.ID,'__EVENTVALIDATION'))).get_attribute('value')

    data_param = {
        '__EVENTTARGET': target,
        '__EVENTARGUMENT': str(num) if num != 1 else '',
        '__LASTFOCUS': '',
        '__VIEWSTATE': viewstate,

        '__VIEWSTATEGENERATOR': viewstategenerator,
        '__VIEWSTATEENCRYPTED': '',
        '__EVENTVALIDATION': eventvalidation,
        'MoreInfoList1$txtProjectName': '',
        'MoreInfoList1$txtBiaoDuanName': '',
        'MoreInfoList1$txtBiaoDuanNo': '',
        'MoreInfoList1$txtJSDW': '',
        'MoreInfoList1$StartDate': '',
        'MoreInfoList1$EndDate': '',
        'MoreInfoList1$jpdDi': '-1',
        'MoreInfoList1$jpdXian': '-1',}

    driver_info = webdriver.DesiredCapabilities.CHROME

    try:
        if "--proxy" in driver_info['goog:chromeOptions']['args'][0]:

            proxy_ip = driver_info['goog:chromeOptions']['args'][0].split('=')[1].split('://')
            proxies = {proxy_ip[0]: proxy_ip[1]}
            page = requests.post(driver.current_url, data=data_param, proxies=proxies,timeout=60).text
        else:
            page = requests.post(driver.current_url, data=data_param,timeout=60).text
    except:
        time.sleep(random.randint(3,5))
        page = requests.post(driver.current_url, data=data_param,timeout=60).text

    data = []
    body = etree.HTML(page)
    content_list = body.xpath('//table[contains(@id,"_DataGrid1")]//tr')
    for content in content_list:
        name = content.xpath("./td/a/@title")[0].strip()
        url = "http://www.jszb.com.cn/jszb/YW_info" + \
              re.findall(r'\(\"\.\.(.*?)\"', content.xpath("./td/a/@onclick")[0].strip())[0]
        project_type = content.xpath("./td[last()-1]/text()")[0].strip()
        ggstart_time = content.xpath("./td[last()]/text()")[0].strip()
        info = json.dumps({"project_type":project_type},ensure_ascii=False)
        temp = [name, ggstart_time, url, info]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, '//font[@color="red"][2]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_temp = driver.find_element_by_xpath('//font[@color="red"][2]').text
    total_page = re.findall(r'\/(\d+)', total_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//table[@id="Table1"]')
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
    div = soup.find('table', id='Table1')
    return div

def query_button(driver):
    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//input[contains(@id,'btnOK')]")))
    ele = driver.find_element_by_xpath("//input[contains(@id,'btnOK')]")
    driver.execute_script('arguments[0].click()', ele)

def query_all(driver):
    """
    查询所有数据
    :param driver:
    :return:
    """
    temp_page = int(re.findall(r'\/(\d+)', WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//font[@color="red"][2]'))).text)[0])
    if 'MoreInfo_ZBGG' in driver.current_url:
        if temp_page <10000:query_button(driver)
    elif 'MoreInfo_ZGXJ' in driver.current_url:
        if temp_page <1300:query_button(driver)
    elif 'MoreInfo_ZBGS' in driver.current_url:
        if temp_page <10000:query_button(driver)
    elif 'MoreInfo_HxrGS' in driver.current_url:
        if temp_page <3000:query_button(driver)
    else:query_button(driver)



    # WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, '//table[contains(@id,"_DataGrid1")]//tr')))


def before(f):
    def inner(*args):
        driver = args[0]
        query_all(driver)
        return f(*args)

    return inner


data1 = [
    ["gcjs_zhaobiao_gg",
     "http://www.jszb.com.cn/jszb/YW_info/ZhaoBiaoGG/MoreInfo_ZBGG.aspx?categoryNum=012&target=MoreInfoList1$Pager",
     # 17581   11000
     ["name", "ggstart_time", "href", "info"], before(f1), before(f2)],
    ["gcjs_kongzhijia_gg",
     "http://www.jszb.com.cn/jszb/YW_info/ZuiGaoXJ/MoreInfo_ZGXJ.aspx?categoryNum=012&target=MoreInfoList1$Pager",
     # 9522   16
     ["name", "ggstart_time", "href", "info"], before(f1), before(f2)],

    ["gcjs_zhongbiao_gg",
     "http://www.jszb.com.cn/jszb/YW_info/ZhongBiaoGS/MoreInfo_ZBGS.aspx?categoryNum=012&target=MoreInfoList1$Pager",
     # 16472   5000
     ["name", "ggstart_time", "href", "info"], before(f1), before(f2)],

    ["gcjs_zhongbiaohx_gg",
     "http://www.jszb.com.cn/jszb/YW_info/HouXuanRenGS/MoreInfo_HxrGS.aspx?categoryNum=012&target=MoreInfoList_HXRGS1$Pager",
     # 7376   0
     ["name", "ggstart_time", "href", "info"], before(f1), before(f2)],

    ["gcjs_zgysjg_gg",
     "http://www.jszb.com.cn/jszb/YW_info/ZiGeYS/MoreInfo_ZGYS.aspx?categoryNum=012&target=MoreInfoList1$Pager",  #2815     1
     ["name", "ggstart_time", "href", "info"], before(f1), before(f2)],

    ["gcjs_gqita_pbjg_gg",
     "http://www.jszb.com.cn/jszb/YW_info/PBJieGuoGS/MoreInfo_PBJieGuoGS.aspx?categoryNum=012&target=MoreInfoList1$Pager",  #12
     ["name", "ggstart_time", "href", "info"], add_info(before(f1),{'Tag':'评标结果'}), before(f2)],

    ["gcjs_gqita_dbjg_gg",
     "http://www.jszb.com.cn/jszb/YW_info/DBJieGuoGS/MoreInfo_DBJieGuoGS.aspx?categoryNum=012&target=MoreInfoList1$Pager", #3
     ["name", "ggstart_time", "href", "info"], add_info(before(f1),{'Tag':'定标结果'}), before(f2)],

    ["gcjs_zhongbiao_1_gg",
     "http://www.jszb.com.cn/JSZB/yw_info/pdfenligs/moreinfo_pdflgs.aspx?categoryNum=012&target=MoreInfoList1$Pager",
     ["name", "ggstart_time", "href", "info"], add_info(before(f1),{'Tag':'评定分离'}), before(f2)],

    ["gcjs_zhaobiao_zjfb_gg",
     "http://www.jszb.com.cn/jszb/YW_info/OtherInfo/MoreInfo_Zjfb.aspx?categoryNum=012&target=MoreInfoList_Zjfb1$Pager",  # 2704  0
     ["name", "ggstart_time", "href", "info"], add_info(before(f1),{'Tag':'直接发包'}), before(f2)],

    ["gcjs_gqita_pmchange_gg",
     "http://www.jszb.com.cn/jszb/YW_info/OtherInfo/MoreInfo_PMC.aspx?categoryNum=012&target=MoreInfoList_PMC1$Pager", #7
     ["name", "ggstart_time", "href", "info"], add_info(before(f1),{'Tag':'项目经理变更'}), before(f2)],

    ["gcjs_yucai_gg",
     "http://www.jszb.com.cn/jszb/YW_info/YuGongShi/MoreInfo_YuGongShi.aspx?categoryNum=012&target=MoreInfoList1$Pager",
     ["name", "ggstart_time", "href", "info"], before(f1), before(f2)],



]


def work(conp, **args):
    est_meta(conp, data=data1, diqu="江苏省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":


    for da in data1:
        try:
            target = parse_qs(da[1]).get('target')[0]
            print(target)
        except:print(da[0])
    # conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "jiangsu"]
    # work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://www.jszb.com.cn/jszb/YW_info/ZhaoBiaoGG/MoreInfo_ZBGG.aspx")
    # before(f1(driver, 2))
    # before(f1)(driver, 10)
    # print(f2(driver))
    # print(before(f2)(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://www.jszb.com.cn/jszb/YW_info/ZhaoBiaoGG/ViewReportDetail.aspx?RowID=658544&categoryNum=012&siteid=1'))
    # driver.close()
    # url = "http://www.jszb.com.cn/jszb/YW_info/ZhaoBiaoGG/MoreInfo_ZBGG.aspx?categoryNum=012&target=MoreInfoList1$Pager"

