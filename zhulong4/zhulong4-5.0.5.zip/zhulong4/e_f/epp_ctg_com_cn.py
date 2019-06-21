import math
import re
import json
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

_name_ = 'epp_ctg_com_cn'


def f1(driver, num):
    num -= 1
    url = re.sub('page=\d+', 'page=' + str(num), driver.current_url)
    # print(url)
    driver.get(url)
    time.sleep(0.1)
    page = driver.page_source
    page_json = json.loads(re.sub(r"\<[^>]+>", "", page))
    content_list = page_json['rows']

    if "zbgg" in driver.current_url:
        type = "ZBGG"
    elif "change" in driver.current_url:
        type = "CQBG"
    elif "ZBGS" in driver.current_url:
        type = "ZBHX"
    elif "result" in driver.current_url:
        type = "ZBJG"
    elif "exception" in driver.current_url:

        type = "YCTZ"
    elif "project" in driver.current_url:

        type = "CGGG"
    data = []
    for content in content_list:
        name = content['TITLE']
        if "exception" in driver.current_url:
            column_id = content['COLUMN_ID']
            typefor = '&typeFor='+column_id
        else:
            typefor = '&typeFor=undefined'
        # http://epp.ctg.com.cn/infoview/?fileId=8087c48092e1404fbc1991a6099e71be&openFor=ZBGG&typeFor=undefined
        url = 'http://epp.ctg.com.cn/infoview/?fileId=%s'%(content['ARTICLE_ID'] if "change" not in driver.current_url else content['ARTICLE_CHANGE_ID']) + "&openFor=" + type+typefor
        try:
            ggstart_time = content['CREATED_TIME']
        except:
            ggstart_time =  content['CREAT_TIME']
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print('temp', temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    page = driver.page_source
    page_json = json.loads(re.sub(r"\<[^>]+>", "", page))
    total_page = page_json['totalPages']
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    if "无法获取查询数据，请重试。" in driver.page_source:
        return "无法获取查询数据，请重试。"
    locator = (By.XPATH, '//body[@dir="LTR"]|/html/body/div[@class="container"]')
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    frame = driver.find_element_by_id('myPanel')
    driver.switch_to.frame(frame)
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
    div = soup.find('body')
    # if div == None:
    # div = soup.find('html')
    if len(div) < 1:
        driver.switch_to.default_content()
        page = driver.page_source
        soup = BeautifulSoup(page, 'lxml')
        div = soup.find('div', class_='ibox')
    driver.switch_to.default_content()

    return div


data = [
    ["qy_zhaobiao_gg",
     "http://epp.ctg.com.cn/index/getData.do?queryName=ctg.list.zbgg&page=0&rows=15",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_biangeng_gg",
     "http://epp.ctg.com.cn/index/getData.do?queryName=ctg.query.change&page=0&rows=15",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_zhongbiaohx_gg",
     "http://epp.ctg.com.cn/index/getData.do?queryName=ctg.result.query&page=0&rows=15",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_zhongbiao_gg",
     "http://epp.ctg.com.cn/index/getData.do?queryName=ctg.ZBGS.query&page=0&rows=15",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qy_liubiao_gg",
     "http://epp.ctg.com.cn/index/getData.do?queryName=ctg.exception&page=0&rows=15",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qy_zhaobiao_cg_gg",
     "http://epp.ctg.com.cn/index/getData.do?queryName=ctg.project.query.unbid&page=1&rows=15",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'采购公告'}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="中国三峡电子采购平台", **args)
    est_html(conp, f=f3, **args)

def main():
    conp = ["postgres", "since2015", "192.168.3.171", "anbang_qiye", "epp_ctg_com_cn"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://epp.ctg.com.cn/index/getData.do?queryName=ctg.project.query.unbid&page=1&rows=15")
    # print(f1(driver, 2))
    # print(f1(driver, 3))
    # f1(driver, 8)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # driver.get("http://ecp.sgcc.com.cn/news_list.jsp?site=global&column_code=014001008&company_id=00&news_name=all&pageNo=1")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 8)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://epp.ctg.com.cn/infoview/?fileId=aacd4d7e842c40f38e46150230aec176&openFor=CQBG'))
    # print(1111111)
    # print(f3(driver, 'http://epp.ctg.com.cn/infoview/?fileId=00356c2d8df74ae5be91c08a1c14a0a9&openFor=CQBG'))
    # print(2222222222222)
    # print(f3(driver, 'http://epp.ctg.com.cn/infoview/?fileId=c32d7abb0df74627982bea25d7cf2870&openFor=ZBHX'))
    # print(1111111)
    # print(f3(driver, 'http://epp.ctg.com.cn/infoview/?fileId=39376699ddfb46639da0482e3d056eec&openFor=YCTZ&typeFor=LB'))
    # print(1111111)
    # print(f3(driver, 'http://epp.ctg.com.cn/infoview/?fileId=e65828f91e86483080351aebdb186c44&openFor=CQBG'))
    # driver.close()
if __name__ == "__main__":
    main()