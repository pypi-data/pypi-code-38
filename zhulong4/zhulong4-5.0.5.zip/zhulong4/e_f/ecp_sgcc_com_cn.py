import json
import math
import re

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

_name_ = 'ecp_sgcc_com_cn'


def f1(driver, num):
    # driver.set_window_size(1366,768)
    locator = (By.XPATH, '//table[@class="font02 tab_padd8"]/tbody/tr[not(@style)]|//ul[@class="newslist01"]/li')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath(
        '//table[@class="font02 tab_padd8"]/tbody/tr[not(@style)][1]/td[last()-1]/a|//ul[@class="newslist01"]/li[1]/a').get_attribute(
        "onclick")[-20:]
    if "column_code" in driver.current_url:
        cnum = driver.find_element_by_xpath('//div[@class="page"]/a[@class="selected"]').text
    else:
        cnum = 1
    # print(val,cnum)
    if int(cnum) != int(num):
        url = re.sub(r'pageNo=\d+', 'pageNo=' + str(num), driver.current_url)
        # print(url)
        driver.get(url)
        locator = (By.XPATH,
                   '//table[@class="font02 tab_padd8"]/tbody/tr[not(@style)][1]/td[last()-1]/a[not(contains(@onclick,"%s"))]|//ul[@class="newslist01"]/li[1]/a[not(contains(@onclick,"%s"))]' % (
                   val, val))
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@class="font02 tab_padd8"]/tbody/tr[not(@style)]|//ul[@class="newslist01"]/li')
    for content in content_list:
        name = content.xpath('./td[last()-1]/a/@title|./a/@title')[0].strip()
        company = content.xpath('./td[last()-1]/a/text()|./a/text()')[0].strip().split(']')[0].strip('[')
        url_temp = '/'.join(re.findall("\'([^\']+)\'", content.xpath('./td[last()-1]/a/@onclick|./a/@onclick')[0].strip()))
        ggstart_time = content.xpath('./td[last()]/text()|./span/text()')[0].strip()
        if "newslist01" not in page:
            code = content.xpath('./td[2]/text()')[0].strip()
            status = content.xpath('./td[1]/text()')[0].strip()
            url = 'http://ecp.sgcc.com.cn/html/project/' + url_temp + '.html'
            info = json.dumps({'code': code, 'company': company, "status": status}, ensure_ascii=False)
        elif "column_code" not in driver.current_url:
            url = "http://ecp.sgcc.com.cn/html/news/" + url_temp + '.html'
            info = json.dumps({"": ''}, ensure_ascii=False)
        else:
            url = 'http://ecp.sgcc.com.cn/html/news/' + url_temp + '.html'
            info = json.dumps({"company": company}, ensure_ascii=False)

        temp = [name, ggstart_time, url, info]
        data.append(temp)
        # print('temp', temp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    # driver.execute_script("window.scrollBy(0,document.body.scrollHeight)", "")
    # driver.execute_script("javascript:getBidList('151','-1',1);")
    if "column_code" in driver.current_url:
        locator = (By.XPATH, '//div[@class="page"]/a[last()-1]')
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        total_page = driver.find_element_by_xpath('//div[@class="page"]/a[last()-1]').text
    else:
        total_page = 1
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="article"]|//div[@class="edit_con_original"]')
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
    div = soup.find('div', class_='article')
    if div == None:
        div = soup.find('div', class_='edit_con_original')
    return div


data = [
    ["qy_zhaobiao_hw_gg",
     "http://ecp.sgcc.com.cn/project_list.jsp?site=global&column_code=014001001&project_type=1&company_id=&status=&project_name=&pageNo=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'type':'货物'}), f2],
    ["qy_zhaobiao_hw_fzb_gg",
     "http://ecp.sgcc.com.cn/news_list.jsp?site=global&column_code=014001008&company_id=00&news_name=all&pageNo=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'type':'货物','Tag':'非招标'}), f2],
    ["qy_zhongbiaohx_hw_gg",
     "http://ecp.sgcc.com.cn/news_list.jsp?site=global&column_code=014001003&company_id=00&news_name=all&pageNo=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'type':'货物'}), f2],
    ["qy_zhongbiao_hw_gg",
     "http://ecp.sgcc.com.cn/news_list.jsp?site=global&column_code=014001007&company_id=00&news_name=all&pageNo=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'type':'货物'}), f2],
    ["qy_gqita_hw_foujuegg_gg",
     "http://ecp.sgcc.com.cn/news_list.jsp?site=global&column_code=014001005&company_id=00&news_name=all&pageNo=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'type':'货物','Tag':'否决公告'}), f2],
    ["qy_gqita_hw_ggxx_gg",
     "http://ecp.sgcc.com.cn/news_list.jsp?site=global&column_code=014001006&company_id=00&news_name=all&pageNo=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'type':'货物','Tag':'公告信息'}), f2],
    ["qy_gqita_hw_nianducaigouanpai_gg",
     "http://ecp.sgcc.com.cn/html/news/global/014001009_00/list_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'type':'货物','Tag':'年度采购安排'}), f2],

    ["qy_zhaobiao_fw_gg",
     "http://ecp.sgcc.com.cn/project_list.jsp?site=global&column_code=014002007&project_type=2&company_id=&status=&project_name=&pageNo=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'type':'服务'}), f2],
    ["qy_zhaobiao_fw_fzb_gg",
     "http://ecp.sgcc.com.cn/news_list.jsp?site=global&column_code=014002008&company_id=00&news_name=all&pageNo=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'type':'服务','Tag':'非招标'}), f2],
    ["qy_zhongbiaohx_fw_gg",
     "http://ecp.sgcc.com.cn/news_list.jsp?site=global&column_code=014002009&company_id=00&news_name=all&pageNo=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'type':'服务'}), f2],
    ["qy_zhongbiao_fw_gg",
     "http://ecp.sgcc.com.cn/news_list.jsp?site=global&column_code=014002003&company_id=00&news_name=all&pageNo=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'type':'服务'}), f2],
    ["qy_gqita_fw_foujuegg_gg",
     "http://ecp.sgcc.com.cn/news_list.jsp?site=global&column_code=014002006&company_id=00&news_name=all&pageNo=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'type':'服务','Tag':'否决公告'}), f2],
    ["qy_gqita_fw_ggxx_gg",
     "http://ecp.sgcc.com.cn/news_list.jsp?site=global&column_code=014002005&company_id=00&news_name=all&pageNo=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'type':'服务','Tag':'公告信息'}), f2],
    ["qy_gqita_fw_nianducaigouanpai_gg",
     "http://ecp.sgcc.com.cn/html/news/global/014002010_00/list_1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'type':'服务','Tag':'年度采购安排'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="国家电网有限公司", **args)
    est_html(conp, f=f3, **args)


def main():
    conp = ["postgres", "since2015", "192.168.3.171", "anbang_qiye", "ecp_sgcc_com_cn"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://ecp.sgcc.com.cn/project_list.jsp?site=global&column_code=014001001&project_type=1&company_id=&status=&project_name=&pageNo=1")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 8)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # driver.get("http://ecp.sgcc.com.cn/news_list.jsp?site=global&column_code=014001008&company_id=00&news_name=all&pageNo=1")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 8)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://ecp.sgcc.com.cn/html/news/014001008/7900000000000075773.html'))
    # print(f3(driver, 'http://ecp.sgcc.com.cn/html/news/014001003/66870.html'))
    # print(f3(driver, 'http://ecp.sgcc.com.cn/html/news/014001008/7900000000000072997.html'))
    # driver.close()


if __name__ == "__main__":
    main()
