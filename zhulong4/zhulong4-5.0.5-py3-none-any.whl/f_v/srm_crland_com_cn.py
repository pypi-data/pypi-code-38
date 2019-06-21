import time

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json

from zhulong4.util.etl import est_tbs, est_meta, est_html

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url = "http://www.fqztb.com/Home/tenderList?index=3&type=%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE"
# driver = webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_ = 'srm_crland_com_cn'


def f1(driver, num):
    num=82+num
    locator = (By.XPATH, '//div[@class="table"]//tbody[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//div[@id="pageControl"]').text
    cnum = re.findall('当前第(.+?)页', cnum)[0].strip()
    url=driver.current_url


    if num != int(cnum):
        val = driver.find_element_by_xpath('//div[@class="table"]//tbody[2]//a').get_attribute('onclick')[21:27]

        if 'toCallNoticePage' in url:

            driver.execute_script("""
                (function goPage(page){
                var orgName = $("#orgName").val().trim();
                var noitceTitle = $("#noitceTitle").val().trim();
                var publishDateStrat = $("#publishDateStrat").val().trim();
                var publishDateEnd = $("#publishDateEnd").val().trim();
                $("#callNotice").load(ctx+"/notice/getCallNoticePageListBySearch.do?"+Math.random(),{orgName:orgName,noitceTitle:noitceTitle,publishDateStrat:publishDateStrat,publishDateEnd:publishDateEnd,page:page,rows:20});
                })(%d)""" % num)
        elif 'toBibNoticePage' in url:
            driver.execute_script("""
            (function goPage(page){
            var orgName = $("#orgName").val().trim();
            var noitceTitle = $("#noitceTitle").val().trim();
            $("#bibNotice").load(ctx+"/notice/getBibNoticePageListBySearch.do?"+Math.random(),{orgName:orgName,noitceTitle:noitceTitle,page:page,rows:20});
            })(%d)"""%num)
        else:
            driver.execute_script("""
            (function goPage(page){
                var orgName = $("#orgName").val().trim();
                var noitceTitle = $("#noitceTitle").val().trim();
                var publishDateStrat = $("#publishDateStrat").val().trim();
                var publishDateEnd = $("#publishDateEnd").val().trim();
                $("#callNotice").load(ctx+"/notice/getCallNoticePageListBySearch.do?"+Math.random(),{orgName:orgName,noitceTitle:noitceTitle,publishDateStrat:publishDateStrat,publishDateEnd:publishDateEnd,page:page,rows:20});
                })(%d)""" % num)


        locator = (By.XPATH, '//div[@class="table"]//tbody[2]//a[not(contains(@onclick,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='table').find_all('tbody')[1:]

    for tr in div:
        tds = tr.find_all('td')
        if len(tds)==8:
            index_num=tds[0].get_text()
            name = tds[1]['title']
            ggstart_time = tds[2].get_text()
            company = tds[3].get_text().strip()
            ggend_time = tds[4].get_text().strip()
            href = tds[5].a['onclick']
            info={"index_num":index_num,'company':company,'ggend_time':ggend_time}


        elif len(tds)==5:
            index_num=tds[0].get_text()
            name = tds[1]['title']
            ggstart_time = tds[3].get_text()
            company = tds[2].get_text().strip()
            href = tds[4].a['onclick']
            info = {'index_num':index_num,'company': company}

        else:
            index_num=tds[0].get_text()
            name = tds[1]['title']
            ggstart_time = tds[3].get_text()
            company = tds[2].get_text().strip()
            gg_type=tds[4].get_text().strip()
            href = tds[5].a['onclick']
            info = {"index_num":index_num,'company': company,"gg_type":gg_type}

        try:
            href_str = re.findall("lookUpBidNoticeFlie\('(.+?)','.+?','(.+?)'\);", href,re.S)[0]
        except:
            print('href 解析错误')
            continue

        href = 'http://srm.crland.com.cn/crland-isp/notice/getBidNoticeFlieList.do?announcementId={mark_id}&noticeType={mark_str}'.format(
            mark_id=href_str[0], mark_str=href_str[1])
        info = json.dumps(info, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)

    df = pd.DataFrame(data=data)


    return df


def f2(driver):

    locator = (By.XPATH, '//div[@class="table"]//tbody[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//div[@id="pageControl"]').text
    total = re.findall('共(.+?)页', total)[0].strip()

    total = int(total)

    driver.quit()

    return total




def f3(driver, url):
    driver.get(url)


    locator = (By.XPATH,
               '//table[@id="materialListTable"][string-length()>10]')

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    time.sleep(0.1)
    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 10: break

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    div = soup.find('table', id="materialListTable")


    return div


data = [

    ["qy_zhaobiao_gg", "http://srm.crland.com.cn/crland-isp/notice/toCallNoticePage.do",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_zhongbiao_gg", "http://srm.crland.com.cn/crland-isp/notice/toBibNoticePage.do",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_liubiao_gg", "http://srm.crland.com.cn/crland-isp/notice/toDiscardbPage.do",["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="华润集团-华润置地", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch3", "srm_crland_com_cn"],headless=False,num=1,cdc_total=10)
    pass