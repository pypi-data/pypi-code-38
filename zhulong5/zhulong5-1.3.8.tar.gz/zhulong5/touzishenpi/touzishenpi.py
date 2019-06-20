import sqlite3
from queue import Queue
import pymssql
import datetime
import psycopg2
import re
import requests
import time
from bs4 import BeautifulSoup
from lxml import etree
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong5.util.etl import est_meta, est_html_cdc

from selenium import webdriver

_name_ = "touzishenpi"



def f4(driver, start_time, end_time):
    try:
        # 去弹窗，否则无头模式影响点击查询
        driver.find_element_by_xpath('//img[@class="demoIcon"]').click()
        # print("点击icon")
        time.sleep(1)
    except:
        pass
    try:
        iframe1 = driver.find_element_by_id("iframepage")
        driver.switch_to.frame(iframe1)
        # print("switch to frame")
    except:
        pass
    locator = (By.XPATH, '//form[@id="serviceForm"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    # 点击全国项目
    driver.find_element_by_xpath('//option[@id="03"]').click()
    # 筛选起始时间
    driver.find_element_by_xpath('//input[@id="apply_date_begin"]').click()
    real_start_time = driver.find_element_by_xpath('//*[@id="apply_date_begin"]').get_attribute("realvalue")
    # print("real_start_time",real_start_time)
    if real_start_time != start_time:
        start_time = start_time.replace('_', '-')
        end_time = end_time.replace('_', '-')
        # print(start_time,end_time)
        driver.find_element_by_xpath('//input[@id="apply_date_begin"]').clear()
        driver.find_element_by_xpath('//input[@id="apply_date_begin"]').send_keys(start_time)
        # print("enter start_end:",start_time)
        end_time_date = driver.find_element_by_xpath('//*[@id="apply_date_end"]').text
        # while end_time_date == datetime.datetime.now().strftime("%Y-%m-%d"):
        driver.find_element_by_xpath('//input[@id="apply_date_end"]').clear()
        driver.find_element_by_xpath('//input[@id="apply_date_end"]').send_keys(end_time)
        driver.find_element_by_xpath('//input[@id="apply_date_end"]').clear()
        driver.find_element_by_xpath('//input[@id="apply_date_end"]').send_keys(end_time)
        # print(end_time_date)
            # end_time_date = driver.find_element_by_xpath('//*[@id="apply_date_end"]').text
        driver.find_element_by_xpath('//input[@id="btnQuery"]').click()


def f1(driver, num):
    locator = (By.XPATH, '//ul[@style="border-bottom: 0;"]/table/tbody/tr[2]/td[@width="350px"]/a')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath(
        '//ul[@style="border-bottom: 0;"]/table/tbody/tr[2]/td[@width="350px"]/a').get_attribute('onclick')[-50:]
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    cnum = driver.find_element_by_xpath('//input[@id="pageNum"]').get_attribute('value')
    if int(cnum) != int(num):
        time.sleep(6)
        driver.execute_script("""goPage(%s);""" % num)
        locator = (By.XPATH, '//ul[@style="border-bottom: 0;"]/table/tbody/tr[2]/td[@width="350px"]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    page = driver.page_source
    body = etree.HTML(page)
    data = []
    content_list = body.xpath('//ul[@style="border-bottom: 0;"]/table/tbody/tr[position()!=1]')
    for content in content_list:
        xiangmu_code = content.xpath("./td[@width='290px']/a/text()")[0].strip().strip("【").strip("】")
        name = content.xpath("./td[@width='350px']/@title")[0]
        ggstart_time = content.xpath("./td[last()]/text()")[0].replace('/', '-')
        url = "https://www.tzxm.gov.cn:8081" + re.findall(r"'([^']+?)'", content.xpath("./td[@width='290px']/a/@onclick")[0])[0]
        shenpishixiang = content.xpath('./td[@width="270px"]/@title')[0]
        shenpibumen = content.xpath('./td[@width="210px"]/text()')[0]
        status = content.xpath('./td[@width="80px"]/text()')[0]
        temp = [name, ggstart_time, url, xiangmu_code, shenpishixiang, shenpibumen, status]
        data.append(temp)
    # print('val',val,'num',num)
    df = pd.DataFrame(data=data)
    df["info"] = None

    return df


def f2(driver):
    total = driver.find_element_by_xpath("//div[@class='qmanu']").text
    total_page = re.findall("共(\d+)页", total.replace(' ', ''))[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='tab00']|//div[@id='regmain']")
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
    div = soup.find('div', id='tab00')
    if div == None:
        div = soup.find('div', id='regmain')

    return div


def wrapper(f, start_time, end_time):
    def inner(*args):
        driver = args[0]
        f4(driver, start_time, end_time)
        return f(*args)

    return inner


def data_single_append(data_single,start_time,end_time):
    url = "https://www.tzxm.gov.cn:8081/tzxmspweb/tzxmweb/pages/portal/publicinformation/examine_new.jsp"

    """
    构建data
    :param data_single:data表
    :param start_time: 开始时间
    :param end_time:结束时间
    :return:
    """
    cols_list = ["name", "ggstart_time", "href", "xiangmu_code", "shenpishixiang", "shenpibumen", "status", "info"]

    data_single.append("quanguoxiangmu_" + start_time + '_' + end_time + '_gg')
    data_single.append(url)
    data_single.append(cols_list)
    data_single.append(wrapper(f1, start_time, end_time))
    data_single.append(wrapper(f2, start_time, end_time))
    return data_single



def get_data_list():
    # 按照时间为爬取界限。
    time_range = [
        ['2003_01_01', '2004_01_01'],
        ['2006_01_01', '2007_01_01'],
        ['2007_01_01', '2008_01_01'],
        ['2008_01_01', '2009_01_01'],
        ['2009_01_01', '2010_01_01'],
        ['2010_01_01', '2011_01_01'],
        ['2011_01_01', '2012_01_01'],
        ['2012_01_01', '2013_01_01'],
        ['2013_01_01', '2014_01_01'],
        ['2014_01_01', '2015_01_01'],
        ['2015_01_01', '2016_01_01'],
        ['2016_01_01', '2017_01_01'],
        # 哪一年开始分月份抓取数据，则写到哪一年为止。2016年开始分月抓取，则写到2016_01_01,2017_01_01
    ]
    time_range_q = Queue()

    for i in time_range:
        time_range_q.put(i)
    data = []
    while not time_range_q.empty():
        data_single = []
        try:
            temp = time_range_q.get(block=False)
            start_time,end_time = temp[0],temp[1]
        except:
            return
        if start_time >= '2016_01_01' and start_time < end_time:
            # 从2016年开始数据按照每个月份来抓取
            # start_time_month = datetime.datetime.strptime(start_time,'%Y_%m_%d').month
            while start_time >= '2016_01_01' and int(start_time.split('_')[1]) <= 12 and start_time < str(
                    time.strftime("%Y_%m_%d", time.localtime(time.time()))):
                data_single = []
                start_time_month = datetime.datetime.strptime(start_time, '%Y_%m_%d').month
                if start_time_month < 12:
                    if 1 <= start_time_month < 9:
                        end_time = re.sub(r'_(\d+)_', '_' + '0' + str(int(start_time.split('_')[1]) + 1) + '_', start_time)
                    else:
                        end_time = re.sub(r'_(\d+)_', '_' + str(int(start_time.split('_')[1]) + 1) + '_', start_time)
                else:
                    end_time = str(datetime.datetime.strptime(start_time, '%Y_%m_%d').year + 1) + '_01_01'
                data_single = data_single_append(data_single,start_time,end_time)
                data.append(data_single)
                start_time, end_time = end_time, start_time

        else:
            data_single = data_single_append(data_single, start_time, end_time)
            data.append(data_single)
    return data



def work(conp, **arg):
    """
    针对：html爬取
        增加 limit 参数（减轻数据库查询压力，加快速度）：每轮爬取 page 的限制。默认 1000
        增加 turn 参数（减轻数据库查询压力，加快速度）：page 爬取的轮数。默认10
        以上两个数据可以根据机器性能进行更改。
    :param conp:
    :param arg:
    :return:
    """
    est_meta(conp, data=data, diqu="全国", **arg)
    est_html_cdc(conp, f=f3, **arg)


data = get_data_list()
# print(data)
if __name__ == "__main__":

    conp = ["postgres", "since2015", "192.168.3.171", "anbang", "touzishenpi111"]
    work(conp,limit=500,turn=5)
