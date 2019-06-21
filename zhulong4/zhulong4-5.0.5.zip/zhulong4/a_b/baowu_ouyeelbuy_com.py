import json
import math
import random
import re

import requests
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong4.util.etl import est_html, est_meta, add_info, est_meta_large
import time

_name_ = 'baowu_ouyeelbuy_com'


def f1(driver, num):
    time.sleep(random.randint(3,6))
    locator = (By.XPATH, '//table[@border="border"]/tbody/tr/td')
    WebDriverWait(driver, 60).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//table[@border="border"]/tbody/tr[1]/td/a').get_attribute("href")[-40:]
    cnum = driver.find_element_by_xpath('//span[@class="current"]').text
    if int(cnum) != int(num):
        if 'biddingNotice' in driver.current_url:
            driver.execute_script("javascript:newsList('0',%s)" % num)
        elif "moreListb" in driver.current_url:
            driver.execute_script("javascript:newsList('bid',%s)" % num)
        else:
            driver.execute_script("javascript:newsList('purchase',%s)" % num)

        locator = (By.XPATH, '//table[@border="border"]/tbody/tr[1]/td/a[not(contains(@href,"%s"))]' % val)
    WebDriverWait(driver, 60).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@border="border"]/tbody/tr')
    for content in content_list:
        info_temp={}
        name = content.xpath('./td[3]/a/text()')[0].strip()
        buyer_name = content.xpath('./td[2]/span/text()|./td[2]/text()')[0].strip()
        info_temp['buyer_name'] = buyer_name

        url = content.xpath('./td[3]/a/@href')[0].strip()
        ggstart_time = content.xpath('./td[last()]/text()')[0].strip()
        # print(ggstart_time)
        ggstart_time = content.xpath('./td[last()]/text()')[0].strip().split(' ')[0]
        if "moreListb" in driver.current_url:
            bid_winner_supplier = content.xpath('./td[5]/text()')[0].strip()
            bid_winner_money = content.xpath('./td[6]/text()')

            info_temp['bid_winner_supplier'] = bid_winner_supplier
            info_temp['bid_winner_money'] = bid_winner_money

            info = json.dumps(info_temp,ensure_ascii=False)
            temp = [name, ggstart_time, url,info]

        elif "moreLista" in driver.current_url:
            # 此页面的最后一个td代表的是截止时间，倒数第二是开始时间
            deadline = content.xpath('./td[last()-1]/text()')[0].strip()
            info_temp['deadline'] = deadline
            info = json.dumps(info_temp,ensure_ascii=False)
            temp = [name,  ggstart_time, url,info]
        else:
            info = json.dumps(info_temp,ensure_ascii=False)

            temp = [name, ggstart_time, url,info]
        data.append(temp)
        # print('temp', temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, '//a[@id="total"]')
    WebDriverWait(driver, 50).until(EC.presence_of_element_located(locator))
    total_page = driver.find_element_by_xpath('//a[@id="total"]').text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    time.sleep(0.1)
    locator = (By.XPATH,
               '//div[@class="articletext"]|//*[@id="ef_tab_x"]|//body[@class="lan2"]|//div[@class="m-bd"]|//table[@bordercolor="#999999"]|//div[@class="w"]')
    WebDriverWait(driver, 50).until(EC.presence_of_element_located(locator))
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
    div = soup.find('div', class_='articletext')
    if div == None:
        div = soup.find('div', id='ef_tab_x')
        if div == None:  # /html/body/div[2]
            div = soup.find('div', class_='m-bd')
            if div == None:
                div = soup.find('table', bordercolor='#999999')
                if div == None:
                    div = soup.body.find('div', class_='w', recursive=False)
                    if div == None:
                        div = ''.join('%s' % s for s in soup.findAll('body', class_="lan2"))

    return div


data = [
    ["qy_zhaobiao_gg",
     "http://baowu.ouyeelbuy.com/baowu-shp/biddingNotice/biddingNoticeList.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_zhongbiao_gg",
     "http://baowu.ouyeelbuy.com/baowu-shp/biddingNotice/biddingResultList.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_gqita_zhao_bian_gg",
     "http://baowu.ouyeelbuy.com/baowu-shp/biddingNotice/biddingChangeList.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qy_zhaobiao_caigou_gg",
     "http://baowu.ouyeelbuy.com/baowu-shp/moreLista.html",
     ["name", "ggstart_time", 'href', "info"], add_info(f1,{"Tag":"采购"}), f2],
    ["qy_zhongbiao_caigou_gg",
     "http://baowu.ouyeelbuy.com/baowu-shp/moreListb.html",
     ["name", "ggstart_time", 'href', "info"], add_info(f1,{"Tag":"采购"}), f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="中国宝武采购专区", **args)
    est_html(conp, f=f3, **args)


def main():
    conp = ["postgres", "since2015", "192.168.3.171", "anbang_qiye", "baowu_ouyeelbuy_com"]
    work(conp, pageloadtimeout=40)
    # caps = DesiredCapabilities().CHROME
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--no-sandbox')
    # caps["pageLoadStrategy"] = 'normal'
    # args = {'desired_capabilities': caps, 'chrome_options': chrome_options}
    # driver = webdriver.Chrome(**args)
    # driver.get("http://baowu.ouyeelbuy.com/baowu-shp/biddingNotice/biddingNoticeList.html")
    # for i in range(170, 1111): print(f1(driver, i))


if __name__ == "__main__":
    main()
