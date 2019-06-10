import json

import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write, db_command, db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

from zhulong2.util.etl import est_meta, est_html, add_info

_name_ = 'zhejiang_ningbo'


def f3(driver, url):
    driver.get(url)
    # if "Demand" in url:
    try:
        locator = (By.XPATH, '//*[@id="aspnetForm"]/div[4]/table[1]/tbody/tr/td[2]/table[2]/tbody/tr/td/table')
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    except:
        locator = (By.XPATH,
                   '//*[@id="barrierfree_container"]/table[1]/tbody/tr/td/table/tbody/tr/td[3]/table[3]/tbody/tr/td/table')
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
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
    if "Demand" in url:
        div = soup.find('table', attrs={'border': 0, 'cellspacing': 0, 'valign': 'top'})
    elif 'zcy' in url:
        div = soup.find('table', attrs={'width': 763, 'cellspacing': 0, 'align': 'center'})
    else:
        div = soup.find('div', class_='detail_con')
    if not div:
        div = soup.find('table',width='820')
    # print(div)
    return div


def f1(driver, num):
    locator = (By.XPATH,
               '//*[@id="ctl00_ContentPlaceHolder3_gdvNotice3"]/tbody/tr[2]/td[5]/a | //*[@id="ctl00_ContentPlaceHolder3_gdvDemandNotice"]/tbody/tr[2]/td[2]/a|//*[@id="gdvNotice3"]/tbody/tr[2]/td[3]/a')
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath(
        '//*[@id="ctl00_ContentPlaceHolder3_gdvNotice3"]/tbody/tr[2]/td[5]/a | //*[@id="ctl00_ContentPlaceHolder3_gdvDemandNotice"]/tbody/tr[2]/td[2]/a|//*[@id="gdvNotice3"]/tbody/tr[2]/td[3]/a').get_attribute("href")[-30:]
    if "Demand" in driver.current_url:
        cnum = re.findall(r'第(\d+)页', driver.find_element_by_xpath(
            '//*[@id="ctl00_ContentPlaceHolder3_gdvDemandNotice_ctl18_AspNetPager1"]/table/tbody/tr/td[1]/span').text)[
            0]
    elif "zcy" in driver.current_url:
        cnum = re.findall(r'第(\d+)页', driver.find_element_by_xpath(
            '//*[@id="gdvNotice3_ctl18_AspNetPager1"]/table/tbody/tr/td[1]/span').text)[0]

    else:
        cnum = re.findall(r'第(\d+)页', driver.find_element_by_xpath(
            '//*[@id="ctl00_ContentPlaceHolder3_gdvNotice3_ctl18_AspNetPager1"]/table/tbody/tr/td[1]/span').text)[0]
    # print('val', val, 'cnum', cnum)
    if int(cnum) != int(num):
        if "Demand" in driver.current_url:
            driver.execute_script(
                "javascript:__doPostBack('ctl00$ContentPlaceHolder3$gdvDemandNotice$ctl18$AspNetPager1','%s')" % num)
        elif "zcy" in driver.current_url:
            driver.execute_script("javascript:__doPostBack('gdvNotice3$ctl18$AspNetPager1','%s')" % num)

        else:
            driver.execute_script(
                "javascript:__doPostBack('ctl00$ContentPlaceHolder3$gdvNotice3$ctl18$AspNetPager1','%s')" % num)

        locator = (By.XPATH,
                   '//*[@id="ctl00_ContentPlaceHolder3_gdvNotice3"]/tbody/tr[2]/td[5]/a[not(contains(@href,"%s"))] |//*[@id="ctl00_ContentPlaceHolder3_gdvDemandNotice"]/tbody/tr[2]/td[2]/a[not(contains(@href,"%s"))]|//*[@id="gdvNotice3"]/tbody/tr[2]/td[3]/a[not(contains(@href,"%s"))]' % (
                   val, val, val))
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath(
        '//*[@id="ctl00_ContentPlaceHolder3_gdvNotice3"]/tbody/tr[not(position()=last())][not(@style)] | //*[@id="ctl00_ContentPlaceHolder3_gdvDemandNotice"]/tbody/tr[not(position()=last())][not(@style)]|//*[@id="gdvNotice3"]/tbody/tr[not(position()=last())][not(@style)]')

    for content in content_list:

        ggstart_time = content.xpath('./td[last()]/text()')[0].strip()

        if content.xpath('count(./td)') > 4:
            name = content.xpath("./td[5]/a/text()")[0].strip().strip('[').strip(']') + content.xpath("./td[4]/text()")[
                0].strip()
            href = 'http://www.nbzfcg.cn/project/' + content.xpath("./td[5]/a/@href")[0].strip()
            company = content.xpath("./td[2]/a/text()")[0].strip()
            area = content.xpath("./td[1]/a/text()")[0].strip()
            info = json.dumps({'company':company,'area':area},ensure_ascii=False)
            temp = [name, ggstart_time, href,info]
        elif "zcy" in driver.current_url:
            name = content.xpath("./td[3]/a/text()")[0].strip().strip('[').strip(']')
            href = 'http://www.nbzfcg.cn/project/' + content.xpath("./td[3]/a/@href")[0].strip()
            area = content.xpath("./td[1]/text()")[0].strip()
            info = json.dumps({ 'area': area}, ensure_ascii=False)
            temp = [name, ggstart_time, href, info]
        else:
            name = content.xpath("./td[2]/a/text()")[0].strip().strip('[').strip(']')
            href = 'http://www.nbzfcg.cn/project/' + content.xpath("./td[2]/a/@href")[0].strip()
            area = content.xpath("./td[1]/a/text()")[0].strip()
            info = json.dumps({ 'area': area}, ensure_ascii=False)
            temp = [name, ggstart_time, href, info]

        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH,
               '//*[@id="ctl00_ContentPlaceHolder3_gdvNotice3_ctl18_AspNetPager1"]/table/tbody/tr/td[1]/span | //*[@id="ctl00_ContentPlaceHolder3_gdvDemandNotice_ctl18_AspNetPager1"]/table/tbody/tr/td[1]/span|//*[@id="gdvNotice3_ctl18_AspNetPager1"]/table/tbody/tr/td[1]/span')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    if "Demand" in driver.current_url:
        total_page = re.findall(r'共(\d+)页', driver.find_element_by_xpath(
            '//*[@id="ctl00_ContentPlaceHolder3_gdvDemandNotice_ctl18_AspNetPager1"]/table/tbody/tr/td[1]/span').text)[
            0]
    elif "zcy" in driver.current_url:
        total_page = re.findall(r'共(\d+)页', driver.find_element_by_xpath(
            '//*[@id="gdvNotice3_ctl18_AspNetPager1"]/table/tbody/tr/td[1]/span').text)[0]
    else:
        total_page = re.findall(r'共(\d+)页', driver.find_element_by_xpath(
            '//*[@id="ctl00_ContentPlaceHolder3_gdvNotice3_ctl18_AspNetPager1"]/table/tbody/tr/td[1]/span').text)[0]
    driver.quit()
    return int(total_page)


data = [
    #
    ["zfcg_zhaobiao_gg", "http://www.nbzfcg.cn/project/Notice2.aspx?ZFCGFlag=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_qita_gg", "http://www.nbzfcg.cn/project/Notice2.aspx?ZFCGFlag=%E5%85%B6%E4%BB%96%E6%A0%87%E8%AE%AF",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gglx':'其他标讯'}), f2],
    ["zfcg_zhongbiao_gg", "http://www.nbzfcg.cn/project/Notice3.aspx?ZFCGFlag=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zgys_gg", "http://www.nbzfcg.cn/project/Notice1.aspx?ZFCGFlag=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_qita_gg",
     "http://www.nbzfcg.cn/project/Notice3.aspx?ZFCGFlag=%E5%85%B6%E4%BB%96%E6%A0%87%E8%AE%AF",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gglx':'其他标讯'}), f2],
    ["zfcg_zhaobiao_danyilaiyuan_gg", "http://www.nbzfcg.cn/project/DemandNotice.aspx?NoticeType=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_zcy_gg", "http://www.nbzfcg.cn/project/zcyNotice.aspx?noticetype=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"Tag":'政采云'}), f2],
    ["zfcg_zhaobiao_danyilaiyuan_zcy_gg", "http://www.nbzfcg.cn/project/zcyNotice.aspx?noticetype=13",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'单一来源',"Tag":'政采云'}), f2],
    ["zfcg_zhongbiao_zcy_gg", "http://www.nbzfcg.cn/project/zcyNotice.aspx?noticetype=51",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"Tag":'政采云'}), f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="浙江省杭州市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "10.30.30.64", "zfcg", "zhejiang_ningbo"],num=3,headless=False)
    # url = "http://www.nbzfcg.cn/project/DemandNotice_view.aspx?Id=2ef08fa2-c86d-4c57-b2c3-4ec92bb1de4b"
    # driver = webdriver.Chrome()
    # print(f3(driver,'http://www.nbzfcg.cn/project/Notice_view.aspx?Id=23801'))
    # driver.get(url)
    # f1(driver,1)
    # f1(driver,6)
    # print(f2(driver))
    # url = "http://www.nbzfcg.cn/project/DemandNotice.aspx?NoticeType=1"
    # driver = webdriver.Chrome()
    # driver.get(url)
    # f1(driver,1)
    # f1(driver,6)
    # print(f2(driver))
    # url = "http://www.nbzfcg.cn/project/zcyNotice.aspx?noticetype=51"
    # driver = webdriver.Chrome()
    # driver.get(url)
    # f1(driver,1)
    # f1(driver,6)
    # print(f2(driver))
