import pandas as pd
import re

from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write, db_command, db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import json
from zhulong.util.etl import est_html, est_meta, add_info,est_meta_large

_name_ = "hunan"


def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='article-list2']/li")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//ul[@class='pages-list']/li")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    txt = driver.find_element_by_xpath("//ul[@class='pages-list']/li[1]/a").text
    cnum = int(re.findall("([0-9]*)\/[0-9]*页", txt)[0])

    if cnum != num:
        val = driver.find_element_by_xpath("//ul[@class='article-list2']/li[1]/div/a").get_attribute("href")[-40:]
        url = re.sub('queryContent[\-\_\d]*\-', 'queryContent_%s-' % str(num), driver.current_url)

        driver.get(url)
        locator = (By.XPATH, "//ul[@class='article-list2']/li[1]/div/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source

    body = etree.HTML(page)
    contents = body.xpath("//ul[@class='article-list2']/li")
    data = []
    for content in contents:
        name = content.xpath('./div/a')[0].xpath('string(.)').strip()
        href = content.xpath('./div/a/@href')[0].strip()
        ggstart_time = content.xpath('./div/div/text()')[0].strip()
        other_info = content.xpath('./div[2]')[0].xpath('string(.)').replace('\n\t', ',').replace(' ', '').strip(',').replace('\n', '')
        info = {}
        other_info_list = other_info.split(',')
        for i in other_info_list:
            info[i.split('：')[0]] = i.split('：')[1]

        dt = json.dumps(info, ensure_ascii=False)
        tmp = [name, href, ggstart_time, dt]

        data.append(tmp)
        # print(tmp)
    df = pd.DataFrame(data=data)

    # df["info"]=
    return df


def f2(driver):
    locator = (By.XPATH, "//ul[@class='pages-list']/li")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    txt = driver.find_element_by_xpath("//ul[@class='pages-list']/li[1]/a").text

    total = re.findall("[^0-9]*\/([0-9]*)页", txt)[0]
    total = int(total)

    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, "//div[@class='content']")

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

    table = soup.find('div', class_='content')

    # div=div.find_all('div',class_='ewb-article')[0]

    return table


data = [
    # 招标
    ["gcjs_zhaobiao_fjsz_gg",
     "http://www.hnsggzy.com/queryContent-jygk.jspx?title=&origin=&inDates=&channelId=848&ext=%E6%8B%9B%E6%A0%87%2F%E8%B5%84%E5%AE%A1%E5%85%AC%E5%91%8A&beginTime=&endTime=",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {'Tag': '房建市政'}), f2],

    ["gcjs_zhaobiao_gygc_gg",
     "http://www.hnsggzy.com/queryContent-jygk.jspx?title=&origin=&inDates=&channelId=847&ext=%E6%8B%9B%E6%A0%87%2F%E8%B5%84%E5%AE%A1%E5%85%AC%E5%91%8A&beginTime=&endTime=",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {'Tag': '工业工程'}), f2],

    ["gcjs_zhaobiao_slgc_gg",
     "http://www.hnsggzy.com/queryContent-jygk.jspx?title=&origin=&inDates=&channelId=849&ext=%E6%8B%9B%E6%A0%87%2F%E8%B5%84%E5%AE%A1%E5%85%AC%E5%91%8A&beginTime=&endTime=",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {'Tag': '水利工程'}), f2],

    ["gcjs_zhaobiao_jtgc_gg",
     "http://www.hnsggzy.com/queryContent-jygk.jspx?title=&origin=&inDates=&channelId=850&ext=%E6%8B%9B%E6%A0%87%2F%E8%B5%84%E5%AE%A1%E5%85%AC%E5%91%8A&beginTime=&endTime=",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {'Tag': '交通工程'}), f2],

    # 澄清
    ["gcjs_gqita_zhaobiao_cheng_fjsz_gg",
     "http://www.hnsggzy.com/queryContent-jygk.jspx?title=&origin=&inDates=&channelId=848&ext=%E6%8B%9B%E6%A0%87%E6%BE%84%E6%B8%85&beginTime=&endTime=",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {'Tag': '房建市政'}), f2],

    ["gcjs_gqita_zhaobiao_cheng_gygc_gg",
     "http://www.hnsggzy.com/queryContent-jygk.jspx?title=&origin=&inDates=&channelId=847&ext=%E6%8B%9B%E6%A0%87%E6%BE%84%E6%B8%85&beginTime=&endTime=",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {'Tag': '工业工程'}), f2],

    ["gcjs_gqita_zhaobiao_cheng_slgc_gg",
     "http://www.hnsggzy.com/queryContent-jygk.jspx?title=&origin=&inDates=&channelId=849&ext=%E6%8B%9B%E6%A0%87%E6%BE%84%E6%B8%85&beginTime=&endTime=",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {'Tag': '水利工程'}), f2],

    ["gcjs_gqita_zhaobiao_cheng_jtgc_gg",
     "http://www.hnsggzy.com/queryContent-jygk.jspx?title=&origin=&inDates=&channelId=850&ext=%E6%8B%9B%E6%A0%87%E6%BE%84%E6%B8%85&beginTime=&endTime=",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {'Tag': '交通工程'}), f2],

    # 中标候选人公示
    ["gcjs_zhongbiaohx_fjsz_gg",
     "http://www.hnsggzy.com/queryContent-jygk.jspx?title=&origin=&inDates=&channelId=848&ext=%E4%B8%AD%E6%A0%87%E5%80%99%E9%80%89%E4%BA%BA%E5%85%AC%E7%A4%BA&beginTime=&endTime=",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {'Tag': '房建市政'}), f2],

    ["gcjs_zhongbiaohx_gygc_gg",
     "http://www.hnsggzy.com/queryContent-jygk.jspx?title=&origin=&inDates=&channelId=847&ext=%E4%B8%AD%E6%A0%87%E5%80%99%E9%80%89%E4%BA%BA%E5%85%AC%E7%A4%BA&beginTime=&endTime=",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {'Tag': '工业工程'}), f2],

    ["gcjs_zhongbiaohx_slgc_gg",
     "http://www.hnsggzy.com/queryContent-jygk.jspx?title=&origin=&inDates=&channelId=849&ext=%E4%B8%AD%E6%A0%87%E5%80%99%E9%80%89%E4%BA%BA%E5%85%AC%E7%A4%BA&beginTime=&endTime=",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {'Tag': '水利工程'}), f2],

    ["gcjs_zhongbiaohx_jtgc_gg",
     "http://www.hnsggzy.com/queryContent-jygk.jspx?title=&origin=&inDates=&channelId=850&ext=%E4%B8%AD%E6%A0%87%E5%80%99%E9%80%89%E4%BA%BA%E5%85%AC%E7%A4%BA&beginTime=&endTime=",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {'Tag': '交通工程'}), f2],

    # 中标候选人公示
    ["gcjs_zhongbiao_fjsz_gg",
     "http://www.hnsggzy.com/queryContent-jygk.jspx?title=&origin=&inDates=&channelId=848&ext=%E4%B8%AD%E6%A0%87%E7%BB%93%E6%9E%9C%E5%85%AC%E5%91%8A&beginTime=&endTime=",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {'Tag': '房建市政'}), f2],

    ["gcjs_zhongbiao_gygc_gg",
     "http://www.hnsggzy.com/queryContent-jygk.jspx?title=&origin=&inDates=&channelId=847&ext=%E4%B8%AD%E6%A0%87%E7%BB%93%E6%9E%9C%E5%85%AC%E5%91%8A&beginTime=&endTime=",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {'Tag': '工业工程'}), f2],

    ["gcjs_zhongbiao_slgc_gg",
     "http://www.hnsggzy.com/queryContent-jygk.jspx?title=&origin=&inDates=&channelId=849&ext=%E4%B8%AD%E6%A0%87%E7%BB%93%E6%9E%9C%E5%85%AC%E5%91%8A&beginTime=&endTime=",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {'Tag': '水利工程'}), f2],

    ["gcjs_zhongbiao_jtgc_gg",
     "http://www.hnsggzy.com/queryContent-jygk.jspx?title=&origin=&inDates=&channelId=850&ext=%E4%B8%AD%E6%A0%87%E7%BB%93%E6%9E%9C%E5%85%AC%E5%91%8A&beginTime=&endTime=",
     ["name", "href", "ggstart_time", "info"], add_info(f1, {'Tag': '交通工程'}), f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="湖南省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres","since2015","192.168.3.171","hunan","hunan"],pageloadstrategy='none',pageloadtimeout=50,num=2)
    # driver = webdriver.Chrome()
    # driver.get("http://www.hnsggzy.com/queryContent-jygk.jspx?title=&origin=&inDates=&channelId=848&ext=%E6%8B%9B%E6%A0%87%2F%E8%B5%84%E5%AE%A1%E5%85%AC%E5%91%8A&beginTime=&endTime=")
    # print(f3(driver, 'http://hnsbenji.hnsggzy.com/jygksz/660617.jhtml'))
# insert_tb('zfcg_biangen_gg',conp=["postgres","since2015","127.0.0.1","hunan","changde"],diqu="湖南省常德市")
