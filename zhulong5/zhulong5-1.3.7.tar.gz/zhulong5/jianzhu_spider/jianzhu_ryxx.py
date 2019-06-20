# encoding:utf-8
import json
import math
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

from zhulong5.jianzhu_spider import jianzhu_ryxx
from zhulong5.util.conf import get_conp
from zhulong5.util.fake_useragent import UserAgent
from gzqzl.jianzhu_etl import jianzhu_ryxx_est_html

_name_ = "jianzhu"

# --------------------------------------------------------获取多页注册人员内容----------------------------------------------
sema=Semaphore(1)

# 获取多页数据函数
def get_data(soup, proxies):
    conp = get_conp(jianzhu_ryxx._name_)
    divs = soup.find('div', class_='clearfix')
    sf = divs.find('a', attrs={"sf":"pagebar"})['sf:data']
    total = int(re.findall(r'tt:(\d+),', sf)[0])
    if total != 0:
        total_num = math.ceil(total / 25)
    else:
        return '暂未查询到已登记入库信息'
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




def get_f7_data(link, proxies, tnum=3):
    while tnum > 0:
        tnum -= 1
        dat = f7_requests(link, proxies)
        if dat:return dat
    raise ConnectionError



def f7_requests(link, proxies):
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

def f7(driver, arr,proxies):
    ryxx_href, ryxx_nanme, sex, id_type, id_number, zyzcxx, grgcyj, blxw, lhxw, hmdjl, bgjl = None, None, None, None, None, None, None, None, None, None, None
    href = arr[0]
    ryxx_href = arr[1]

    data = []
    page_source = get_f7_data(ryxx_href, proxies)
    soup = BeautifulSoup(page_source, 'html.parser')
    ryxx_name = soup.find("div", class_='user_info spmtop').text.strip()
    sex = soup.find("dd", class_='query_info_dd1').text.strip().split('：')[1]
    id_type = soup.find_all("dd", class_='query_info_dd2')[0].text.strip().split('：')[1]
    id_number = soup.find_all("dd", class_='query_info_dd2')[1].text.strip().split('：')[1]

    list_1 = soup.find('ul', class_='tinyTab datas_tabs')
    list_name = []
    for lis in list_1.find_all('li')[1:]:
        li = lis.find('a')
        if li.find('em'):
            li.find('em').extract()
        span = li.find('span').text.replace(' ','')
        link = li['data-url']
        if span and link:
            data_dict = {'name':span,'link':link}
            list_name.append(data_dict)

    zyzcxx = get_zyzcxx(soup,ryxx_href, proxies)
    if not zyzcxx: raise ValueError
    for li in list_name:
        name = li['name']
        link = 'http://jzsc.mohurd.gov.cn' + li['link']
        if '个人工程业绩' in name:
            grgcyj = get_grgcyj(link, proxies)
            if not grgcyj: raise ValueError
        elif '不良行为' in name:
            blxw = get_blxw(link, proxies)
            if not blxw: raise ValueError
        elif '良好行为' in name:
            lhxw = get_lhxw(link, proxies)
            if not lhxw: raise ValueError
        elif '黑名单记录' in name:
            hmdjl = get_hmdjl(link, proxies)
            if not hmdjl: raise ValueError
        elif '变更记录' in name:
            bgjl = get_bgjl(link, proxies)
            if not bgjl: raise ValueError
    tmp = [href, ryxx_href, ryxx_name, sex, id_type, id_number, str(zyzcxx), str(grgcyj), str(blxw),str(lhxw), str(hmdjl), str(bgjl)]
    data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


# 执业注册信息
def get_zyzcxx(soup,ryxx_href, proxies):
    if soup.find('div', class_='quotes'):
        zyzcxx = get_data(soup, proxies)
        return zyzcxx
    zyzcxx = soup.find('div', id='regcert_tab')
    if "暂未查询到已登记入库信息" in zyzcxx.text.replace(' ', ''):
        dat = get_f7_data(ryxx_href, proxies)
        soup = BeautifulSoup(dat, 'html.parser')
        zyzcxx = soup.find('div', id='regcert_tab')
        if "暂未查询到已登记入库信息" in zyzcxx.text.replace(' ', ''):
            zyzcxx = "暂未查询到已登记入库信息"
    else:
        if soup.find('div', class_='activeTinyTabContent'):
            zyzcxx = soup.find('div', id='regcert_tab')
        else:
            raise ValueError
    return zyzcxx



# 个人工程业绩
def get_grgcyj(link, proxies):
    dat2 = get_f7_data(link, proxies)
    soup2 = BeautifulSoup(dat2, 'html.parser')
    if soup2.find('div', class_='clearfix'):
        grgcyj = get_data(soup2, proxies)
        return grgcyj
    grgcyj = soup2.find('table', class_='pro_table_box pro_table_borderright')
    if "暂未查询到已登记入库信息" in grgcyj.text.replace(' ',''):
        dat2 = get_f7_data(link, proxies)
        soup2 = BeautifulSoup(dat2, 'html.parser')
        grgcyj = soup2.find('table', class_='pro_table_box pro_table_borderright')
        if "暂未查询到已登记入库信息" in grgcyj.text.replace(' ', ''):
            grgcyj = "暂未查询到已登记入库信息"
    else:
        if soup2.find('td', attrs={'data-header': '项目编码'}):
            grgcyj = soup2.find('table', class_='pro_table_box pro_table_borderright')
        else:raise ValueError
    return grgcyj

# 不良行为
def get_blxw(link, proxies):
    dat3 = get_f7_data(link, proxies)
    soup3 = BeautifulSoup(dat3, 'html.parser')
    if soup3.find('div', class_='clearfix'):
        blxw = get_data(soup3, proxies)
        return blxw
    blxw = soup3.find('table', class_='pro_table_box pro_table_borderright')
    if "暂未查询到已登记入库信息" in blxw.text.replace(' ',''):
        blxw = "暂未查询到已登记入库信息"
    else:
        if soup3.find('td', attrs={'data-header': '诚信记录编号'}):
            blxw = soup3.find('table', class_='pro_table_box pro_table_borderright')
        else:raise ValueError
    return blxw


# 良好行为
def get_lhxw(link, proxies):
    dat4 = get_f7_data(link, proxies)
    soup4 = BeautifulSoup(dat4, 'html.parser')
    if soup4.find('div', class_='clearfix'):
        lhxw = get_data(soup4, proxies)
        return lhxw
    lhxw = soup4.find('table', class_='pro_table_box pro_table_borderright')
    if "暂未查询到已登记入库信息" in lhxw.text.replace(' ',''):
        lhxw = "暂未查询到已登记入库信息"
    else:
        if soup4.find('td', attrs={'data-header': '诚信记录主体'}):
            lhxw = soup4.find('table', class_='pro_table_box pro_table_borderright')
        else:raise ValueError
    return lhxw

# 黑名单记录
def get_hmdjl(link, proxies):
    dat5 = get_f7_data(link, proxies)
    soup5 = BeautifulSoup(dat5, 'html.parser')
    if soup5.find('div', class_='clearfix'):
        hmdjl = get_data(soup5, proxies)
        return hmdjl
    hmdjl = soup5.find('table', class_='table_box credit_table')
    if "暂未查询到已登记入库信息" in hmdjl.text.replace(' ',''):
        hmdjl = "暂未查询到已登记入库信息"
    else:
        if soup5.find('td', attrs={'data-header': '黑名单记录主体'}):
            hmdjl = soup5.find('table', class_='table_box credit_table')
        else:raise ValueError
    return hmdjl

# 变更记录
def get_bgjl(link, proxies):
    dat6 = get_f7_data(link, proxies)
    soup6 = BeautifulSoup(dat6, 'html.parser')
    if soup6.find('div', class_='clearfix'):
        bgjl = get_data(soup6, proxies)
        return bgjl
    bgjl = soup6.find('table', class_='pro_table_box')
    if "暂未查询到已登记入库信息" in bgjl.text.replace(' ',''):
        bgjl = "暂未查询到已登记入库信息"
    else:
        if soup6.find('td', attrs={'data-header': '变更记录'}):
            bgjl = soup6.find('table', class_='pro_table_box')
        else:raise ValueError
    return bgjl



dd = ["href", "ryxx_href", "ryxx_name", "sex", "id_type", "id_number", "zyzcxx", "grgcyj", "blxw", "lhxw", "hmdjl", "bgjl"]

def work(conp, **args):
    jianzhu_ryxx_est_html(conp, f=f7, data=dd, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "jianzhu"], pageloadtimeout=180)
    #
    # ip = get_ip()
    # print("本次ip %s" % ip)
    # if re.match("[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}:[0-9]{1,5}", ip) is None:
    #     print("ip不合法")
    # data = [['http://jzsc.mohurd.gov.cn/dataservice/query/comp/compDetail/001607220057358803','http://jzsc.mohurd.gov.cn/dataservice/query/staff/staffDetail/001610081858678559']]
    # # da = pd.DataFrame(data=data)
    # driver = webdriver.Chrome()
    # driver.get('https://www.baidu.com')
    # for d in data:
    #     df = f7(driver, d, proxies={"http": "http://%s" % (ip)})
    #     print(df.values)
    #     print(df.columns, df.dtypes)
