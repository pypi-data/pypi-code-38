# encoding:utf-8
import os
import random
import traceback
from collections import OrderedDict
from multiprocessing import Semaphore
from queue import Queue
from threading import Thread
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from gzqzl.jianzhu_etl import jianzhu_est_meta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zhulong5.util_jianzhu.etl import est_html
from zhulong5.util_jianzhu.fake_useragent import UserAgent
from gzqzl.jianzhu_conf import get_df, jz_db

_name_ = "jianzhu"


tt_url = None
tt = None
num_list = []  # 存放每一项的页数，是累加的
title_list = []  # 存放每一项请求所需要的参数，与num_list是一一对应的
ip_q = Queue()
tmp_q = Queue()
sema=Semaphore(1)

def f1_click(num):
    """
    对列表num_list分类，获取对应项的真实页数
    :param num:
    :return:
    """
    list_num = int(len(num_list))
    for i in range(1, list_num+1):
        if i == 1:
            if num <= num_list[i-1]:
                num = num
                return i-1,num

        else:
            if num_list[i-2] < num <= num_list[i-1]:
                num = num - num_list[i-2]
                return i-1,num


def f1(driver, num, proxies):
    """
    爬取总数据
    :param driver:
    :param num:
    :param proxies:
    :return:
    """
    i,num = f1_click(num)
    total,payloadData = title_list[i][0],title_list[i][1]
    # 因为该网站超过30页是请求不到数据的，故只获取前30页
    if num > 30:
        sema.acquire()
        if type(payloadData).__name__ != 'dict':
            payloadData = eval(payloadData)
        tmps = [total, payloadData]
        get_df(tmps, 'cfg4')
        sema.release()
        return False
    # 判断是否是第一次爬取，如果是增量更新,只获取前5页
    # if num > CDC_NUM:
    #     return
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': user_agent,
        }
    data_dict = {
        "$total": total,
        "$pgsz": 15,
        "$reload": 0,
        "$pg": num,
    }
    Datas = {**data_dict, **payloadData}
    # 下载超时
    timeOut = 60
    sesion = requests.session()
    time.sleep(random.uniform(1, 2))
    res = sesion.post(url=tt_url, headers=headers, data=Datas, timeout=timeOut, proxies=proxies)
    # 需要判断是否为登录后的页面
    if res.status_code != 200:
        raise ConnectionError
    else:
        html = res.text
        html_data = BeautifulSoup(html, 'html.parser')
        tbody = html_data.find('tbody', class_='cursorDefault')
        trs = tbody.find_all('tr')
        data = []
        for tr in trs:
            try:
                td = tr.find('td', class_='text-left complist-num').text.strip()
            except:
                td = '-'
            title = tr.find('td', class_='text-left primary').text.strip()
            href = tr.find('a')['href'].strip()
            link = 'http://jzsc.mohurd.gov.cn'+href
            try:
                person = tr.find_all('td')[-2].text.strip()
            except:
                person = '-'
            try:
                place = tr.find_all('td')[-1].text.strip()
            except:
                place = '-'
            tmp = [td, title, link, person, place]
            data.append(tmp)

        df = pd.DataFrame(data=data)
        df['info'] = None
        return df


def f2(driver):
    """
    获取总页数
    tt_url：http://jzsc.mohurd.gov.cn/dataservice/query/comp/list
    tt:资质类别(例如QY_ZZ_ZZZD_003)
    region：省市与对应的id
    :param driver:
    :return:
    """
    global tt_url,tt,num_list,title_list
    num_list = []
    title_list = []
    tt_url = None
    tt = None
    start_url = driver.current_url
    tt_url = start_url.rsplit('/', maxsplit=1)[0]
    tt = start_url.rsplit('/', maxsplit=1)[1]
    # tt = unquote(tt, encoding='utf-8', errors='replace')
    args = tt.split('&')
    tt_dict = {}
    for arg in args:
        if arg == '':
            continue
        k, v = arg.split('=')
        tt_dict[k] = v
    data_dict = []
    for i in range(100):
        tt_dict_1 = tt_dict.copy()
        qy_code = tt_dict_1['qy_code']
        if len(str(i)) == 1:
            i = '0%s' % i
        m = str(i)
        tt_dict_1['qy_code'] = qy_code+m
        data_dict.append(tt_dict_1)
    # 考虑怎么获取总页数，循环获取
    list_1 = []
    # 多线程获取每一项的页数
    read_threads(get_pageall, 10, data_dict, list_1)
    cnum = sum(list_1)
    for i in range(1, len(list_1) + 1):
        b = sum(list_1[:i])
        num_list.append(b)

    driver.quit()
    return int(cnum)


def read_threads(f, num, data_dict, list_1):
    bg = time.time()
    ths = []
    dfs = []
    total = len(data_dict)
    if total <= 5: num = 1
    if total != 0 and num / total > 1: num = int(total / 5) + 1 if int(total / 5) + 1 < 4 else num
    tmp_q.queue.clear()
    for i in range(total):
        tmp_q.put(i+1)
    print("本次共 %d 个请求,共%d 个线程" % (total, num))
    for _ in range(num):
        t = Thread(target=read_thread, args=(f, data_dict, list_1,))
        ths.append(t)
    for t in ths:
        t.start()
    for t in ths:
        t.join()
    left_page = tmp_q.qsize()
    print("剩余 %d个请求" % (left_page))
    if left_page > 0:
        read_thread(f, data_dict, list_1)
        left_page = tmp_q.qsize()
        print("剩余 %d个请求" % (left_page))
    ed = time.time()
    cost = ed - bg
    if cost < 100:
        print("耗时%d 秒" % cost)
    else:
        print("耗时%.4f 分" % (cost / 60))


def read_thread(f,data_dict, list_1):
    num=5
    flag=__read_thread(f,data_dict, list_1)
    while not flag and  num>0:
        num-=1
        print("切换ip,本线程第%d次"%(5-num))
        print("已经消耗ip %d 个"%ip_q.qsize())
        flag=__read_thread(f,data_dict, list_1)


def __read_thread(f, data_dict, list_1):
    # url=tt_url
    # if self.localhost_q.empty():
    ip=get_ip()
    #ip="1.28.0.90:20455"
    print("本次ip %s"%ip)
    if re.match("[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}:[0-9]{1,5}",ip) is None:
        print("ip不合法")
        return False
    try:
        proxies = {
            "http": "http://%s"%(ip),
        }
        # driver=get_driver(ip)
        # driver.get(url)
    except Exception as e:
        traceback.print_exc()
        # driver.quit()
        return False
    while not tmp_q.empty():
         try:
            x=tmp_q.get(block=False)
         except:
            traceback.print_exc()
            continue
         if x is None:continue
         try:
            bnum=f(tt_url, data_dict[x-1], proxies)
            if bnum == None:
                continue
            if bnum:list_1.append(bnum)
         except Exception as e:
            traceback.print_exc()
            msg=traceback.format_exc()
            print("第 %d 个请求异常"%x)
            if "违反" not in msg:
                tmp_q.put(x)
            # driver.quit()
            return False
    # driver.quit()
    print("线程正常退出")
    return True


def get_ip():
    sema.acquire()
    try:
        url="""http://ip.11jsq.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=0&fa=0&fetch_key=&qty=1&time=1&pro=&city=&port=1&format=txt&ss=1&css=&dt=1&specialTxt=3&specialJson="""
        r=requests.get(url)
        time.sleep(1)
        ip_q.put(r.text)
        ip=r.text
    except:
        ip="ip失败"
    finally:
        sema.release()
    return ip


def get_pageall(tt_url, data_dict, proxies):
    '''
    获取每一项的页数
    :param tt_url:
    :param tt:
    :param data_dict:
    :param title_list:
    :return:
    '''
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': user_agent,
       }

    payloadData = data_dict
    # 下载超时
    timeOut = 60
    sesion = requests.session()
    time.sleep(random.uniform(1, 2))
    res = sesion.post(url=tt_url, headers=headers, data=payloadData, timeout=timeOut, proxies=proxies)
    # 需要判断是否为登录后的页面
    if res.status_code != 200:
        raise ConnectionError
    else:
        html = res.text
        num = re.findall(r'sf:data="(.*)"', html)[0]
        total = re.findall(r'tt:(\d+),', num)[0]
        total = int(total)
        if total != 0:
            if total / 15 == int(total / 15):
                page_all = int(total / 15)
            else:
                page_all = int(total / 15) + 1
        else:
            return None
        title_list.append((total, payloadData))
        return page_all


def f3(driver, url):
    driver.get(url)
    try:
        locator = (By.XPATH, "//div[@class='user_info spmtop']")
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    except:
        driver.refresh()
        time.sleep(random.uniform(1, 2))
        locator = (By.XPATH, "//div[@class='user_info spmtop']")
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))

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

    div1 = soup.find('div', class_='query_info_box ')
    div2 = soup.find('div', class_='plr spmtop')
    div = str(div1) + str(div2)
    div = BeautifulSoup(div, 'html.parser')

    return div



def get_data():
    list1 = jz_db('cfg3')
    data = []
    zztype = OrderedDict([("kancha", "QY_ZZ_ZZZD_003"), ("sheji", "QY_ZZ_ZZZD_004"), ("jianzhu", "QY_ZZ_ZZZD_001"),
                          ("jianli", "QY_ZZ_ZZZD_002"),
                          ("zbdl", "QY_ZZ_ZZZD_006"), ("sjsg", "QY_ZZ_ZZZD_005"), ("zjzx", "QY_ZZ_ZZZD_007")])

    for w1 in list1:
        if type(w1).__name__ != 'list':
            # w1 = w1.split("[")[1].split("]")[0].split(",", maxsplit=1)
            w1 = list(eval(w1))
        if type(w1[1]).__name__ != 'dict':
            w1[1] = eval(w1[1])

        for w2 in zztype.keys():
            if w1[1]['qy_type'] == zztype[w2]:
                p2 = "%s" % (w1[1]['qy_region'])
                p3 = "%s" % (w1[1]['apt_code'])
                args = w1[1]
                query = ''
                for key, value in args.items():
                    query += '%s=%s&' % (key, value)
                href = "http://jzsc.mohurd.gov.cn/dataservice/query/comp/list/%s" % query
                tmp = ["cgjs_%s_dq%s_%s_3_gg" % (w2, p2, p3.lower()), href, ["td", "name", "href", "person", "place", "info"], f1, f2]
                data.append(tmp)

    data1=data.copy()
    remove_arr = []
    for w in data:
        if w[0] in remove_arr:data1.remove(w)
    return data1

data=get_data()


def work(conp, **args):
    jianzhu_est_meta(conp, data=data, diqu="全国", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "jianzhu"],pageloadtimeout=120)

