# encoding:utf-8
import json
import math
import os
import random
from multiprocessing import Semaphore
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from gzqzl.jianzhu_pages import jianzhu_select_pages, jianzhu_insert_pages
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from zhulong5.jianzhu_spider import jianzhu_xmxx
from zhulong5.util.conf import get_conp
from zhulong5.util.fake_useragent import UserAgent
from gzqzl.jianzhu_etl import jianzhu_xmxx_est_html

_name_ = "jianzhu"

# --------------------------------------------------------获取多页注册人员内容----------------------------------------------
sema=Semaphore(1)

# 获取多页数据函数
def get_data(soup, proxies):
    conp = get_conp(jianzhu_xmxx._name_)
    divs = soup.find('div', class_='clearfix')
    sf = divs.find('a', attrs={"sf":"pagebar"})['sf:data']
    total = int(re.findall(r'tt:(\d+),', sf)[0])
    if total != 0:
        total_num = math.ceil(total / 25)
    else:
        return '暂未查询到已入库'
    action = soup.find('form', class_='pagingform')['action']
    link = 'http://jzsc.mohurd.gov.cn' + action
    form = soup.find('div', class_='clearfix').script.text.replace(' ','')
    total = int(re.findall(r'total":(\d+),', form)[0])
    reload = int(re.findall(r'reload":(\d+),', form)[0])
    pgsz = int(re.findall(r'pgsz":(\d+)', form)[0])
    data_dict={'link':link,'total':total,'reload':reload,'pgsz':pgsz}
    # 查询已经获取到的数据
    pages = jianzhu_select_pages(conp, link)
    # print(pages)
    pg_list = []
    if pages != []:
        for p in pages:
            pg = json.loads(p)['pg']
            pg_list.append(int(pg))
    list11 = []
    for dt in range(1, int(total_num) + 1):
        # 不在获取已有数据的页数
        if dt in pg_list:
            continue
        tnum = 3
        while tnum > 0:
            tnum -= 1
            gtd = get_total_data(data_dict, dt, proxies)
            if gtd:
                # 先将数据存放数据库
                jianzhu_insert_pages(conp, data=[link, gtd])
                list11.append(gtd)
                break
            if tnum == 0:
                raise ValueError
    if pages:list11.extend(pages)
    if list11 and 'null' not in list11 and 'false' not in list11:
        list2 = json.dumps(list11, ensure_ascii=False)
        return list2
    else:
        raise ValueError



def get_total_data(data_dict, dt, proxies):
    total = data_dict['total']
    reload = data_dict['reload']
    pgsz = data_dict['pgsz']
    link = data_dict['link']
    payloadData = {
        "$total": total,
        "$reload": reload,
        "$pg": dt,
        "$pgsz": pgsz,
    }
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': user_agent,
    }
    timeOut = 120
    time.sleep(random.uniform(3, 5))
    res = requests.post(url=link, headers=headers, data=payloadData, timeout=timeOut, proxies=proxies)
    # 需要判断是否为登录后的页面
    if res.status_code != 200:
        return False
    html = res.text
    soups = BeautifulSoup(html, 'html.parser')
    trs = soups.find('table')
    if soups.find('table'):
        if "暂未查询到已登记入库信息" in soups.find('table').text.replace(' ',''):
            # print('requests请求失败！')
            return False
        else:
            dt_dict = {'pg':dt,'trs':str(trs)}
            dt_dict = json.dumps(dt_dict, ensure_ascii=False)
            return dt_dict
    else:return False



def get_ip():
    sema.acquire()
    try:
        url="""http://ip.11jsq.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=0&fa=0&fetch_key=&qty=1&time=1&pro=&city=&port=1&format=txt&ss=1&css=&dt=1&specialTxt=3&specialJson="""
        r=requests.get(url)
        time.sleep(1)
        ip=r.text
    except:
        ip="ip失败"
    finally:
        sema.release()
    return ip




def get_f8_data(link, proxies, tnum=3):
    while tnum > 0:
        tnum -= 1
        dat = f8_requests(link, proxies)
        if dat:return dat
    raise ConnectionError



def f8_requests(link, proxies):
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': user_agent,
        }
    timeOut = 120
    time.sleep(random.uniform(1, 2))
    res = requests.get(url=link, headers=headers, timeout=timeOut, proxies=proxies)
    # 需要判断是否为登录后的页面
    if res.status_code != 200:
        return False
    html = res.text
    soups = BeautifulSoup(html, 'html.parser')
    trs = soups.find('body')
    if trs:
        return str(trs)
    else:return False



# ---------------------------------------------------------程序主入口------------------------------------------------------

def f8(driver,arr,proxies):
    href,xmxx_name,xmxx_href,xmxx_page = None,None,None,None
    href = arr[0]
    xmxx_href = arr[1]
    data = []
    page_source = get_f8_data(xmxx_href, proxies)
    soup = BeautifulSoup(page_source, 'html.parser')
    xmxx_name = soup.find('div', class_='user_info spmtop').b['title']

    if soup.find('div', class_='quotes'):
        sema.acquire()
        with open('xmxx.txt', 'a', encoding='utf-8') as ft:
            ft.writelines("%s\n" % [href, xmxx_href])  # "a"就是append的意思,就是有写文件的时候不会覆盖前面的内容后追加到后面.
            ft.flush()
            ft.close()
            sema.release()
        xmxx_page = get_data(soup, proxies)
    elif soup.find('div', class_='activeTinyTabContent'):
        xmxx_page = soup.find('div', class_='main_box nav_mtop')
    else:
        raise ValueError
    tmp = [href,xmxx_name,xmxx_href,str(xmxx_page)]
    data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



dd = ["href","xmxx_name","xmxx_href","xmxx_page"]

def work(conp, **args):
    jianzhu_xmxx_est_html(conp, f=f8, data=dd, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "jianzhu"], pageloadtimeout=180,flag=0)

    # ip = get_ip()
    # print("本次ip %s" % ip)
    # if re.match("[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}:[0-9]{1,5}", ip) is None:
    #     print("ip不合法")
    # data = [['http://jzsc.mohurd.gov.cn/dataservice/query/comp/compDetail/001712270039095228','http://jzsc.mohurd.gov.cn/dataservice/query/project/projectDetail/3311271905230006']]
    # # da = pd.DataFrame(data=data)
    # driver = webdriver.Chrome()
    # driver.get('https://www.baidu.com')
    # for d in data:
    #     df = f8(driver, d, proxies={"http": "http://%s" % (ip)})
    #     print(df.values)
    #     print(df.columns, df.dtypes)
