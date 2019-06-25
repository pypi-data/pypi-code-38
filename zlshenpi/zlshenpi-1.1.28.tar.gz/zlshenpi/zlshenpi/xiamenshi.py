import math

import pandas as pd
import re

import requests
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zlshenpi.util.etl import add_info, est_meta, est_html, est_tbs, add_info, est_meta_large
import sys
import time
import json

from zlshenpi.util.fake_useragent import UserAgent

_name_ = "xiamenshi"


def f1(driver, num):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies = ''
    start_url = 'http://tzzx.xmdpc.gov.cn/json/data/services'
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': user_agent,
        "Content-Type": "application/json",
    }
    payloadData = {
        "serviceName": "cdDataStoreService", "methodName": "loadData", "validate": False, "version": "5.3.1",
        "args": "[{\"dataStoreId\":\"CD_DS_APP_TZXM_SPDW_ITEM_APPROVE_PROJECT_INFO\",\"proxy\":{\"storeId\":\"CD_DS_APP_TZXM_SPDW_ITEM_APPROVE_PROJECT_INFO\"},\"pagingInfo\":{\"pageSize\":\"10\",\"currentPage\":%d,\"autoCount\":true},\"params\":{\"keyword\":\"\"},\"criterions\":[{\"sql\":\"result = 1 gsxx\"}],\"renderers\":[{\"columnIndex\":\"code\",\"param\":{\"rendererName\":\"Freemarker模板渲染器\",\"rendererType\":\"freemarkerTemplateRenderer\",\"template\":\"【${rowData.p_project_code}】\\n</br>\\n【${rowData.p_project_region_code}】\"}},{\"columnIndex\":\"result\",\"param\":{\"rendererName\":\"Freemarker模板渲染器\",\"rendererType\":\"freemarkerTemplateRenderer\",\"template\":\"<if rowData.result == 1>批复<else></if>\"}},{\"columnIndex\":\"modify_time\",\"param\":{\"rendererName\":\"日期渲染器\",\"rendererType\":\"dateRenderer\",\"format\":\"yyyy-MM-dd\"}}],\"orders\":[{\"sortName\":\"modify_time\",\"sortOrder\":\"desc\"}]}]"%(num)
    }
    # 下载超时
    timeOut = 120
    if proxies:
        res = requests.post(url=start_url, headers=headers, data=json.dumps(payloadData), timeout=timeOut, proxies=proxies)
    else:
        res = requests.post(url=start_url, headers=headers, data=json.dumps(payloadData), timeout=timeOut)

    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        html = res.text
        html_data = json.loads(html)
        dats = html_data['data']
        datas = dats['data']
        data = []
        for tr in datas:
            name = tr['p_project_name']
            ggstart_time = tr['modify_timeRenderValue']

            projectUuid = tr['project_uuid']
            itemApprovalUuid = tr['uuid']
            href = 'http://tzzx.xmdpc.gov.cn/tzxm/spdw/publicityquery/view/result?projectUuid='+projectUuid+'&itemApprovalUuid='+itemApprovalUuid

            xm_code = tr['p_project_code']
            xm_difang_code = tr['p_project_region_code']
            shenpishixiang = tr['item_name']
            shenpijieguo = tr['resultRenderValue']
            info = {'xm_code':xm_code,'xm_difang_code':xm_difang_code,'shenpishixiang':shenpishixiang,'shenpijieguo':shenpijieguo}
            info = json.dumps(info, ensure_ascii=False)
            tmp = [name, ggstart_time, href, info]
            data.append(tmp)
        df = pd.DataFrame(data=data)
        return df
    else:
        raise ConnectionError

def f2(driver):
    start_url = 'http://tzzx.xmdpc.gov.cn/json/data/services'
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': user_agent,
        "Content-Type": "application/json",
    }
    payloadData = {
        "serviceName": "cdDataStoreService", "methodName": "loadData", "validate": False, "version": "5.3.1",
         "args": "[{\"dataStoreId\":\"CD_DS_APP_TZXM_SPDW_ITEM_APPROVE_PROJECT_INFO\",\"proxy\":{\"storeId\":\"CD_DS_APP_TZXM_SPDW_ITEM_APPROVE_PROJECT_INFO\"},\"pagingInfo\":{\"pageSize\":\"10\",\"currentPage\":1,\"autoCount\":true},\"params\":{\"keyword\":\"\"},\"criterions\":[{\"sql\":\"result = 1 gsxx\"}],\"renderers\":[{\"columnIndex\":\"code\",\"param\":{\"rendererName\":\"Freemarker模板渲染器\",\"rendererType\":\"freemarkerTemplateRenderer\",\"template\":\"【${rowData.p_project_code}】\\n</br>\\n【${rowData.p_project_region_code}】\"}},{\"columnIndex\":\"result\",\"param\":{\"rendererName\":\"Freemarker模板渲染器\",\"rendererType\":\"freemarkerTemplateRenderer\",\"template\":\"<if rowData.result == 1>批复<else></if>\"}},{\"columnIndex\":\"modify_time\",\"param\":{\"rendererName\":\"日期渲染器\",\"rendererType\":\"dateRenderer\",\"format\":\"yyyy-MM-dd\"}}],\"orders\":[{\"sortName\":\"modify_time\",\"sortOrder\":\"desc\"}]}]"
    }
    # 下载超时
    timeOut = 120
    res = requests.post(url=start_url, headers=headers, data=json.dumps(payloadData), timeout=timeOut)
    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        html = res.text
        html_data = json.loads(html)
        data = html_data['data']
        pagination = data['pagination']
        total = pagination['totalPages']
        num = int(total)
        driver.quit()
        return int(num)
    else:
        raise ConnectionError




def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='handle_result_publicity_detail'][string-length()>30]")
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
    div = soup.find('div', class_='handle_result_publicity_detail')
    return div


data = [

    ["xm_jieguo_gg",
     "http://tzzx.xmdpc.gov.cn/web/app/app-tzxm-home/app-tzxm-home-info.html?selection=C792D60E7C3000013F7E7DA0D1E09F80",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="厦门市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres","since2015","192.168.3.171","zlshenpi","xiamenshi"],pageloadtimeout=120)

    # driver = webdriver.Chrome()
    # for d in data:
    #     driver.get(d[1])
    #     print(d[1])
    #     df = f2(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     df = f1(driver,4)
    #     print(df.values)
    #     for j in df[2].values:
    #         df = f3(driver, j)
    #         print(df)
