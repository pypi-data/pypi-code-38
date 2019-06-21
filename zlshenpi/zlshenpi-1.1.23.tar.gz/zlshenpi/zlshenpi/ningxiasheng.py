import math
import os

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

_name_ = "ningxiasheng"

t_list = []
ua = UserAgent()


proxy = {}


def get_ip():
    global proxy
    try:
        url = """http://ip.11jsq.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=0&fa=0&fetch_key=&qty=1&time=1&pro=&city=&port=1&format=txt&ss=1&css=&dt=1&specialTxt=3&specialJson="""
        r = requests.get(url)
        time.sleep(1)
        ip = r.text
        proxy = {'http': ip}
    except:
        proxy = {}
    return proxy


def requests_hb(post_url):
    global proxy
    driver_info = webdriver.DesiredCapabilities.CHROME
    try:
        if "--proxy" in driver_info['goog:chromeOptions']['args'][0]:
            proxy_ip = driver_info['goog:chromeOptions']['args'][0].split('=')[1]
            response = requests.get(post_url, proxies=proxy_ip, headers={"User-Agent": ua.random, "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"},
                                    timeout=40)
        else:
            if proxy == {}: proxy = get_ip()
            response = requests.get(post_url, headers={"User-Agent": ua.random, "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"}, timeout=40)
    except:
        try:
            response = requests.get(post_url, headers={"User-Agent": ua.random, "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"}, timeout=40,
                                    proxies=proxy)
        except:
            proxy = get_ip()
            response = requests.get(post_url, headers={"User-Agent": ua.random, "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"}, timeout=40,
                                    proxies=proxy)
    return response



def f1_click(num):
    """
    对列表num_list分类，获取对应项的真实页数
    :param num:
    :return:
    """
    list_num = int(len(t_list))
    for i in range(1, list_num + 1):
        if i == 1:
            if num <= t_list[i - 1]['total_page']:
                num = num
                diqu = t_list[i - 1]['diqu']
                href = t_list[i - 1]['href']
                return num,diqu,href

        else:
            if t_list[i - 2]['total_page'] < num <= t_list[i - 1]['total_page']:
                num = num - t_list[i - 2]['total_page']
                diqu = t_list[i - 1]['diqu']
                href = t_list[i - 1]['href']
                return num,diqu,href

def f1(driver, num):
    # print(t_list)
    num, diqu, href=f1_click(num)
    # print(num, diqu, href)
    url = driver.current_url
    if url.rsplit('=', maxsplit=1)[0] not in href:
        driver.get(href)
    locator = (By.XPATH, "//table[@id='table1']/tbody/tr[last()]/td[last()]/a")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='tagContent']/p")
    try:
        txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(re.findall('(\d+)/', txt)[0])
    except:cnum=1
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@id='table1']/tbody/tr[last()]/td[last()]/a").get_attribute('href')[-35:]
        url = re.sub('pageNo=[0-9]+', 'pageNo=%d'%num, url)
        driver.get(url)
        locator = (By.XPATH, "//table[@id='table1']/tbody/tr[last()]/td[last()]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find('table', id='table1').tbody
    trs = table.find_all('tr')
    data = []
    for tr in trs[1:]:
        info = {}
        a = tr.find_all('a')[-1]
        try:
            name = tr.find_all('td')[0]['title'].strip()
        except:
            name = tr.find_all('td')[0].text.strip()

        ggstart_time = tr.find_all('td')[4]['title'].strip()
        fileNo = re.findall(r'fileNo=(.*)', a['href'])[0]
        href = 'http://218.95.165.91:8082/servlet/downloadFileServlet?fileNo='+fileNo
        thing_name = tr.find_all('td')[1]['title'].strip()
        info['thing_name']=thing_name
        pizhunjiguan = tr.find_all('td')[2]['title'].strip()
        info['pizhunjiguan']=pizhunjiguan
        pizhunwenhao = tr.find_all('td')[3]['title'].strip()
        info['pizhunwenhao']=pizhunwenhao
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:info = None
        tmp = [name,  ggstart_time,href,info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    global t_list
    locator = (By.XPATH, "//ul[@class='clearfix']/li/a/span")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
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
    uls = soup.find('div', class_='cont', style="display: block;")
    # print(uls)
    lis = uls.find_all('li')
    t_list = []
    total_page = 0
    for li in lis:
        if li.find('span', class_='don-num'):
            a= li.find('a')
            name = a.text.strip()
            diqu = name.rsplit('(', maxsplit=1)[0]
            href = 'http://218.95.165.91:8082'+a['href']
            total = li.find('span', class_='don-num').text.strip()
            num = int(re.findall(r'\d+', total)[0])
            num = math.ceil(num/10)
            total_page+=num
            t_info = {'diqu':diqu, 'href':href, 'total_page':total_page}
            t_list.append(t_info)
    driver.quit()
    return total_page


def f3(driver, url):
    file_p = os.path.join(os.path.dirname(__file__), 'default_path.txt')
    with open(file_p, 'r') as f: default_path = re.findall('\"([^"]+)\"', f.read())[0]
    # o_url = 'http://www.hntzxm.gov.cn/portal/zcfg/busiotherpublicinfo!selectPublicInfo.action?tn=3'
    # driver.get(o_url)
    if not os.path.exists('%s'%default_path):os.mkdir('%s'%default_path)
    if not os.path.exists('%s%s_files' % (default_path,_name_)): os.mkdir('%s%s_files' %(default_path,_name_))

    id = url.split('=')[-1]
    response = requests_hb(url)
    filename = re.findall('\"([^"]+)\"', response.headers['Content-Disposition'].encode('ISO-8859-1').decode('gb2312'))[0]
    if not os.path.exists('%s%s_files/%s_%s' % (default_path,_name_, id, filename)):
        with open('%s%s_files/%s_%s' % (default_path,_name_, id, filename), 'wb') as f:
            f.write(response.content)
    div = '文件保存为 %s%s_files/%s_%s' % (default_path, _name_,id, filename)
    return div


def piqian(f):
    def warp(*krg):
        driver = krg[0]
        locator = (By.XPATH, "//div[@class='don-tab clearfix']/ul/li[@class='active']")
        txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
        if txt !='投资项目批前公示':
            locator = (By.XPATH, "//div[@class='don-tab clearfix']/ul/li[contains(string(), '投资项目批前公示')]")
            WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).click()
            locator = (By.XPATH, "//div[@class='don-tab clearfix']/ul/li[@class='active'][contains(string(), '投资项目批前公示')]")
            WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
        return f(*krg)
    return warp


def pihou(f):
    def warp(*krg):
        driver = krg[0]
        locator = (By.XPATH, "//div[@class='don-tab clearfix']/ul/li[@class='active']")
        txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
        if txt !='投资项目批后公开':
            locator = (By.XPATH, "//div[@class='don-tab clearfix']/ul/li[contains(string(), '投资项目批后公开')]")
            WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).click()
            locator = (By.XPATH, "//div[@class='don-tab clearfix']/ul/li[@class='active'][contains(string(), '投资项目批后公开')]")
            WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
        return f(*krg)
    return warp




data = [
    ["xm_pihou_duqu1_gg",
     "http://218.95.165.91:8082/indexlink/xxgk.jspx?shareaId=640000&sareaId=640100&type=1",
     ["name", "ggstart_time", "href", "info"], add_info(pihou(f1), {'diqu':'银川市'}), pihou(f2)],

    ["xm_pihou_duqu2_gg",
     "http://218.95.165.91:8082/indexlink/xxgk.jspx?shareaId=640000&sareaId=640200&type=1",
     ["name", "ggstart_time", "href", "info"], add_info(pihou(f1), {'diqu': '石嘴山市'}), pihou(f2)],

    ["xm_pihou_duqu3_gg",
     "http://218.95.165.91:8082/indexlink/xxgk.jspx?shareaId=640000&sareaId=640300&type=1",
     ["name", "ggstart_time", "href", "info"], add_info(pihou(f1), {'diqu': '吴忠市'}), pihou(f2)],

    ["xm_pihou_duqu4_gg",
     "http://218.95.165.91:8082/indexlink/xxgk.jspx?shareaId=640000&sareaId=640400&type=1",
     ["name", "ggstart_time", "href", "info"], add_info(pihou(f1), {'diqu': '固原市'}), pihou(f2)],

    ["xm_pihou_duqu5_gg",
     "http://218.95.165.91:8082/indexlink/xxgk.jspx?shareaId=640000&sareaId=640500&type=1",
     ["name", "ggstart_time", "href", "info"], add_info(pihou(f1), {'diqu': '中卫市'}), pihou(f2)],

    ["xm_pihou_duqu6_gg",
     "http://218.95.165.91:8082/indexlink/xxgk.jspx?shareaId=640000&sareaId=640900&type=1",
     ["name", "ggstart_time", "href", "info"], add_info(pihou(f1), {'diqu': '宁东能源化工基地'}), pihou(f2)],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="宁夏省", **args)
    est_html(conp, f=f3, **args)


# 详情页为pdf
if __name__ == '__main__':
    work(conp=["postgres","since2015","192.168.3.171","zlshenpi","ningxiasheng"],pageloadtimeout=120)


    # driver = webdriver.Chrome()
    # for d in data:
    #     driver.get(d[1])
    #     print(d[1])
    #     df = pihou(f2)(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     driver.maximize_window()
    #     df = pihou(f1)(driver,121)
    #     print(df.values)
    #     for j in df[2].values:
    #         df = f3(driver, j)
    #         print(df)
