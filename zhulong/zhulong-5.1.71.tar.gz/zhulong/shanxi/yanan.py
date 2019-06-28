import pandas as pd
import re
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


_name_="yanan"



def f1(driver, num):
    locator = (By.XPATH, "(//div[@class='ewb-right-block l'])[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//a[@class='wb-page-default wb-page-number wb-page-family']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = str.split('/')[0]
    except:
        cnum = 1

    if num != int(cnum):
        val = driver.find_element_by_xpath("(//div[@class='ewb-right-block l'])[1]/a").get_attribute('href')[-40:]
        driver.execute_script("ShowAjaxNewPage(window.location.pathname,'categorypagingcontent',{})".format(num))
        locator = (By.XPATH, "(//div[@class='ewb-right-block l'])[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("div", class_='categorypagingcontent')
    ul = table.find("ul")
    trs = ul.find_all("li", class_='ewb-right-item clearfix')
    data = []
    for tr in trs:
        a = tr.find("a")
        try:
            title = a["title"].strip()
        except:
            title = a.text.strip()
        try:
            link = a["href"]
        except:
            link = '-'
        span = tr.find("span", class_="r").text.strip()
        links = "http://www.yaggzyjy.cn"+link.strip()
        tmp = [title, span, links]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "(//div[@class='ewb-right-block l'])[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//a[@class='wb-page-default wb-page-number wb-page-family']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = str.split('/')[1]
    except:
        num = 1
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='article-block'][string-length()>40]")
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
    div = soup.find('div', class_="article-block")
    return div


data = [
    ["gcjs_zhaobiao_fwjz_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001001/004001001001/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'房屋建筑'}), f2],

    ["gcjs_zgys_fwjz_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001001/004001001002/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'房屋建筑'}), f2],

    ["gcjs_biangeng_fwjz_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001001/004001001003/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'房屋建筑'}), f2],

    ["gcjs_zhongbiao_fwjz_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001001/004001001004/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'房屋建筑'}), f2],
    # #
    ["gcjs_zhaobiao_shizheng_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001002/004001002001/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'市政'}), f2],

    ["gcjs_zgys_shizheng_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001002/004001002002/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'市政'}), f2],

    ["gcjs_biangeng_shizheng_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001002/004001002003/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'市政'}), f2],

    ["gcjs_zhongbiao_shizheng_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001002/004001002004/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'市政'}), f2],
    # #
    ["gcjs_zhaobiao_gonglu_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001003/004001003001/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'公路'}), f2],

    ["gcjs_zgys_gonglu_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001003/004001003002/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'公路'}), f2],

    ["gcjs_biangeng_gonglu_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001003/004001003003/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'公路'}), f2],

    ["gcjs_zhongbiao_gonglu_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001003/004001003004/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'公路'}), f2],
    # #
    ["gcjs_zhaobiao_shuili_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001007/004001007001/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'水利'}), f2],

    ["gcjs_zgys_shuili_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001007/004001007002/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'水利'}), f2],

    ["gcjs_biangeng_shuili_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001007/004001007003/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'水利'}), f2],

    ["gcjs_zhongbiao_shuili_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001007/004001007004/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'水利'}), f2],
    # #
    ["gcjs_zhaobiao_tdzl_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001008/004001008001/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'土地整理'}), f2],

    ["gcjs_zgys_tdzl_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001008/004001008002/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'土地整理'}), f2],

    ["gcjs_biangeng_tdzl_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001008/004001008003/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'土地整理'}), f2],

    ["gcjs_zhongbiao_tdzl_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001008/004001008004/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'土地整理'}), f2],
    # #
    ["gcjs_zhaobiao_qita_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001011/004001011001/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'其他'}), f2],

    ["gcjs_zgys_qita_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001011/004001011002/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'其他'}), f2],

    ["gcjs_biangeng_qita_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001011/004001011003/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'其他'}), f2],

    ["gcjs_zhongbiao_qita_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004001/004001011/004001011004/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'其他'}), f2],

    ["zfcg_zhaobiao_huowu_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004007/004007001/004007001001/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'货物类'}), f2],

    ["zfcg_zhongbiao_huowu_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004007/004007001/004007001003/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'货物类'}), f2],
    #
    ["zfcg_zhaobiao_gongcheng_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004007/004007002/004007002001/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'工程类'}), f2],

    ["zfcg_zhongbiao_gongcheng_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004007/004007002/004007002003/",
     ["name", "ggstart_time", "href", "info"],  add_info(f1,{'gclx':'工程类'}), f2],
    #
    ["zfcg_zhaobiao_fuwu_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004007/004007003/004007003001/",
     ["name", "ggstart_time", "href", "info"],  add_info(f1,{'gclx':'服务类'}), f2],

    ["zfcg_zhongbiao_fuwu_gg",
     "http://www.yaggzyjy.cn/Front_YanAn/jyxx/004007/004007003/004007003003/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'服务类'}), f2],
]


def work(conp,**args):
    est_meta(conp,data=data,diqu="陕西省延安市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shanxi","yanan"])





