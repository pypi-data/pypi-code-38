import math
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
from gzqzl.jianzhu_conf import get_df, jz_db
from gzqzl.jianzhu_etl import jianzhu_est_meta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

import time

from zhulong5.util.conf import get_conp
from zhulong5.util_jianzhu.etl import est_html, gg_existed
from zhulong5.util_jianzhu.fake_useragent import UserAgent

_name_ = "jianzhu"

tt_url = None
tt = None
num_list = []  # 存放每一项的页数，是累加的
title_list = []  # 存放每一项请求所需要的参数，与num_list是一一对应的
ip_q = Queue()
tmp_q = Queue()
sema = Semaphore(1)


def f1_click(num):
    """
    对列表num_list分类，获取对应项的真实页数
    :param num:
    :return:
    """
    list_num = int(len(num_list))
    for i in range(1, list_num + 1):
        if i == 1:
            if num <= num_list[i - 1]:
                num = num
                return i - 1, num

        else:
            if num_list[i - 2] < num <= num_list[i - 1]:
                num = num - num_list[i - 2]
                return i - 1, num


def f1(driver, num, proxies):
    """
    爬取总数据
    :param driver:
    :param num:
    :param proxies:
    :return:
    """
    i, num = f1_click(num)
    total, payloadData = title_list[i][0], title_list[i][1]
    # 判断是否是第一次爬取，如果是增量更新,只获取前5页
    if num > CDC_NUM:
        return
    # 因为该网站超过30页是请求不到数据的，故只获取前30页
    if num > 30:
        sema.acquire()
        # 存放每一项页数超过30的信息，以待后续处理
        if type(payloadData).__name__ != 'dict':
            payloadData = eval(payloadData)
        tmps = [total, payloadData]
        get_df(tmps, 'cfg')
        sema.release()
        return False
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
    time.sleep(random.uniform(1, 2))
    res = requests.post(url=tt_url, headers=headers, data=Datas, timeout=timeOut, proxies=proxies)
    # 需要判断是否为登录后的页面
    if res.status_code != 200:
        raise ConnectionError
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
        link = 'http://jzsc.mohurd.gov.cn' + href
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
    global tt_url, tt, num_list, title_list
    num_list = []
    title_list = []
    tt_url = None
    tt = None
    start_url = driver.current_url
    tt_url = start_url.rsplit('/', maxsplit=2)[0]
    tt = start_url.rsplit('/', maxsplit=2)[1]
    regions = start_url.rsplit('/', maxsplit=2)[2]
    qy_region = re.findall(r'qy_region=(.*),', regions)[0]
    qy_reg_addr = re.findall(r'qy_reg_addr=(.*)', regions)[0]
    region = {'qy_region': qy_region, 'qy_reg_addr': qy_reg_addr}
    # 按省市获取资质类别种类
    data_dict = get_dict(driver, region)
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
        tmp_q.put(i + 1)
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


def read_thread(f, data_dict, list_1):
    num = 5
    flag = __read_thread(f, data_dict, list_1)
    while not flag and num > 0:
        num -= 1
        print("切换ip,本线程第%d次" % (5 - num))
        print("已经消耗ip %d 个" % ip_q.qsize())
        flag = __read_thread(f, data_dict, list_1)


def __read_thread(f, data_dict, list_1):
    # url=tt_url
    # if self.localhost_q.empty():
    ip = get_ip()
    # ip="1.28.0.90:20455"
    print("本次ip %s" % ip)
    if re.match("[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}:[0-9]{1,5}", ip) is None:
        print("ip不合法")
        return False
    try:
        proxies = {
            "http": "http://%s" % (ip),
        }
    except Exception as e:
        traceback.print_exc()
        return False
    while not tmp_q.empty():
        try:
            x = tmp_q.get(block=False)
        except:
            traceback.print_exc()
            continue
        if x is None: continue
        try:
            bnum = f(tt_url, tt, data_dict[x - 1], proxies)
            if bnum == None:
                continue
            if bnum:list_1.append(bnum)
        except Exception as e:
            traceback.print_exc()
            msg = traceback.format_exc()
            print("第 %d 个请求异常" % x)
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
        url = """http://ip.11jsq.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=0&fa=0&fetch_key=&qty=1&time=1&pro=&city=&port=1&format=txt&ss=1&css=&dt=1&specialTxt=3&specialJson="""
        r = requests.get(url)
        time.sleep(1)
        ip_q.put(r.text)
        ip = r.text
    except:
        ip = "ip失败"
    finally:
        sema.release()
    return ip


def get_pageall(tt_url, tt, data_dict, proxies):
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
    Data_dict = {
        "qy_type": tt,
        "qy_name": "",
        "qy_code": "",
        "apt_certno": "",
        "qy_fr_name": "",
        "qy_gljg": "",
    }
    payloadData = {**Data_dict, **data_dict}
    # 下载超时
    timeOut = 60
    time.sleep(random.uniform(1, 2))
    res = requests.post(url=tt_url, headers=headers, data=payloadData, timeout=timeOut, proxies=proxies)
    # 需要判断是否为登录后的页面
    if res.status_code != 200:
        raise ConnectionError
    html = res.text
    num = re.findall(r'sf:data="(.*)"', html)[0]
    total = re.findall(r'tt:(\d+),', num)[0]
    total = int(total)
    if total != 0:
        page_all = math.ceil(total / 15)
    else:
        return None
    title_list.append((total, payloadData))
    return page_all



def get_dict(driver, region):
    '''
    验证是否为字典，不是则转换
    :param driver:
    :param region:
    :return:
    '''
    kinds = get_kind(driver, tt)
    time.sleep(random.uniform(0.5, 1))
    data_list = []
    for w1 in kinds:
        if type(region).__name__ != 'dict':
            region = eval(region)
        elif type(w1).__name__ != 'dict':
            w1 = eval(w1)
        d_dict = {**region, **w1}
        data_list.append(d_dict)
    return data_list


def get_kind(driver, kurl):
    """
    获取资质类别
    :param driver:
    :param kurl:
    :return:
    """
    kind_url = 'http://jzsc.mohurd.gov.cn/asite/qualapt/aptData?apt_type={}'.format(kurl)
    driver.get(kind_url)
    locator = (By.XPATH, "//tr[@class='data_row']")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    apt_data = []
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        a = soup.find('a', attrs={'sf': 'pagebar'})
        dt = a['sf:data']
        dt_total = int(re.findall(r'tt:(\d+),', dt)[0])
    except:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        trs = soup.find_all('tr', class_='data_row')
        for tr in trs:
            apt = tr.find('input', class_='icheck')['value']
            # {"apt_code":"B20302B", "apt_scope":"工程勘察岩土工程专业（岩土工程设计）乙级"}
            apt_data.append(apt)
        return apt_data
    try:
        dt_num = int(driver.find_element_by_xpath("//div[@class='quotes']/a[last()]").get_attribute('dt'))
    except:
        dt_num = 1
    for dt in range(1, dt_num + 1):
        user_agents = UserAgent()
        user_agent = user_agents.chrome
        headers = {
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent': user_agent,
        }
        payloadData = {
            "$total": dt_total,
            "$reload": 0,
            "$pg": dt,
            "$pgsz": 10,
        }
        # 下载超时
        timeOut = 60
        time.sleep(random.uniform(1, 3))
        res = requests.post(url=kind_url, headers=headers, data=payloadData, timeout=timeOut)
        # 需要判断是否为登录后的页面
        if res.status_code != 200:
            raise ConnectionError
        else:
            html = res.text
            soup = BeautifulSoup(html, 'html.parser')
            trs = soup.find_all('tr', class_='data_row')
            for tr in trs:
                apt = tr.find('input', class_='icheck')['value']
                # {"apt_code":"B20302B", "apt_scope":"工程勘察岩土工程专业（岩土工程设计）乙级"}
                apt_data.append(apt)
    return apt_data


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


def get_region():
    """
    获取行政区域划分
    :return:
    """
    region_url = 'http://jzsc.mohurd.gov.cn/asite/region/index'
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': user_agent,
    }
    # 下载超时
    timeOut = 60
    time.sleep(random.uniform(1, 2))
    res = requests.post(url=region_url, headers=headers, timeout=timeOut)
    # 需要判断是否为登录后的页面
    if res.status_code != 200:
        raise ConnectionError
    else:
        html = res.text
        html_data = json.loads(html)
        provinces = html_data['json']['category']['provinces']
        datas = []
        for province in provinces:
            pdict = {}
            pdict["qy_reg_addr"] = province["region_fullname"]
            pdict["qy_region"] = province["region_id"]
            datas.append(pdict)
        return datas


def get_data():
    data = []
    regions = get_region()
    zztype = OrderedDict([("kancha", "QY_ZZ_ZZZD_003"), ("sheji", "QY_ZZ_ZZZD_004"), ("jianzhu", "QY_ZZ_ZZZD_001"),
                          ("jianli", "QY_ZZ_ZZZD_002"),
                          ("zbdl", "QY_ZZ_ZZZD_006"), ("sjsg", "QY_ZZ_ZZZD_005"), ("zjzx", "QY_ZZ_ZZZD_007")])

    for w1 in regions:
        for w2 in zztype.keys():
            p1 = "%s" % (zztype[w2])
            p2 = "%s" % (w1['qy_region'])
            href = "http://jzsc.mohurd.gov.cn/dataservice/query/comp/list/%s/qy_region=%s,qy_reg_addr=%s" % (
                p1, p2, w1['qy_reg_addr'])
            tmp = ["cgjs_%s_dq%s_gg" % (w2, w1['qy_region']), href, ["td", "name", "href", "person", "place", "info"], f1,
                   f2]
            data.append(tmp)

    data1 = data.copy()
    remove_arr = []
    for w in data:
        if w[0] in remove_arr: data1.remove(w)
    return data1


data = get_data()


if gg_existed(conp=get_conp(_name_)):
    CDC_NUM = 5
else:
    CDC_NUM = 10000


# CDC_NUM 为增量更新页数,设置成总页数以上(如:10000)可爬全部
# 增量更新时,需将cdc_total设置成 None

def work(conp, **args):
    jianzhu_est_meta(conp, data=data, diqu="全国", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "jianzhu"],cdc_total=None, pageloadtimeout=120,num=50)
