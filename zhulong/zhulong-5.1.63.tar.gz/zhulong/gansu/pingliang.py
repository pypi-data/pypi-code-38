import random
from collections import OrderedDict
from pprint import pprint

import pandas as pd
import re

import requests
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
from zhulong.util.etl import gg_meta,gg_html,est_meta,est_html
from zhulong.util.fake_useragent import UserAgent

from zhulong.util.etl import add_info


_name_='pingliang'



def f1(driver,num):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        if proxies_chromeOptions:
            proxy = proxies_chromeOptions[0].split('=')[1]
            proxies = {'http': '%s' % proxy}
        else:
            proxies = {}
    except:
        proxies = {}

    ua=UserAgent()

    url_list=driver.current_url.split('?lch?')
    req_url=url_list[0]
    listType=url_list[1].split('=')[1]
    projectType=url_list[2].split('=')[1]
    tradestatus = url_list[3].split('=')[1]

    form_data = {
        "pageNo": num,
        "pageSize": 20,
        "tradeStatus": tradestatus,
        "listType": listType,
        "projectType": projectType,
        "tradeArea": None,
        "projectname": None,
    }

    headers = {
        "Referer": "http://www.plsggzyjy.cn/f/newtrade/annogoods/list",
        "User-Agent": ua.chrome}

    time.sleep(0.5 + random.random())
    req = requests.post(req_url, data=form_data, headers=headers,proxies=proxies, timeout=20)
    if req.status_code != 200:
        raise ValueError('response status_code is %s'%req.status_code)
    data=[]
    soup = BeautifulSoup(req.text, 'html.parser')
    dls = soup.find_all('dl', class_='byTradingDetailParent clear')
    for dl in dls:
        name = dl.find('a').get_text().strip().replace('\n', '').replace('\t', '').replace(' ', '')
        href = dl.find('a')['href']
        ggstart_time = dl.find('span', class_='byTradingDetailTime').get_text()
        href = 'http://www.plsggzyjy.cn' + href
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 

def f2(driver):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        if proxies_chromeOptions:
            proxy = proxies_chromeOptions[0].split('=')[1]
            proxies = {'http': '%s' % proxy}
        else:
            proxies = {}
    except:
        proxies = {}

    ua = UserAgent()
    url_list = driver.current_url.split('?lch?')
    req_url = url_list[0]
    listType = url_list[1].split('=')[1]
    projectType = url_list[2].split('=')[1]
    tradestatus=url_list[3].split('=')[1]

    form_data = {
        "pageNo": 1,
        "pageSize": 20,
        "tradeStatus": tradestatus,
        "listType": listType,
        "projectType": projectType,
        "tradeArea": None,
        "projectname": None,
    }

    headers = {
        "Referer": "http://www.plsggzyjy.cn/f/newtrade/annogoods/list",
        "User-Agent": ua.chrome}

    req = requests.post(req_url, data=form_data, headers=headers,proxies=proxies, timeout=20)
    if req.status_code != 200:
        raise ValueError('response status_code is %s' % req.status_code)

    soup = BeautifulSoup(req.text, 'html.parser')

    total = soup.find_all('li', class_='paginate_button ')
    if total:
        total = int(total[-1].get_text())
    else:
        total = 1

    driver.quit()
    return total


def f3(driver,url):

    driver.get(url)

    locator=(By.XPATH,'//div[@class="jxTradingMainLayer clear"][string-length()>100] | //div[@id="content"][string-length()>50]')

    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    before=len(driver.page_source)
    time.sleep(0.1)
    after=len(driver.page_source)
    i=0
    while before!=after:
        before=len(driver.page_source)
        time.sleep(0.1)
        after=len(driver.page_source)
        i+=1
        if i>5:break

    page=driver.page_source

    soup=BeautifulSoup(page,'html.parser')

    div=soup.find('div',class_='jxTradingMainLayer clear')
    if not div:
        div=soup.find('div',id="content")

    
    return div



def get_data():
    data = []

    pro_list = ['fangjian', 'shizheng', 'jiaotong','shuili','zfcg','zfcg_xiane','gcjs_xiane']

    projecttype = OrderedDict([("fangjian","2"),("shizheng", "3"), ("jiaotong", "4,5,6,7"),
                               ("shuili","8"),('zfcg','21,22,23,24'),('gcjs_xiane','10'),('zfcg_xiane','11')])

    gc_dict={'gcjs_xiane':'engineer','zfcg_xiane':'gover'}

    projecttype_old = OrderedDict([("fangjian", "1"), ("shizheng", "2"), ("jiaotong", "3"),
                               ("shuili", "4"), ('zfcg', '5')])

    prozw_dict=OrderedDict([("fangjian","房建工程"),("shizheng", "市政工程"), ("jiaotong", "交通工程"),
                            ("shuili","水利工程"),('gcjs_xiane','限额以下'),('zfcg_xiane','限额以下')])

    listtype = OrderedDict([("zgys", "1"),("zhaobiao","2"),("kongzhijia", "3"), ("biangeng", "4"),
                            ("zgysjg", "5"),("zhongbiaohx","6"),("liubiao", "7")])

    listtype_xiane= OrderedDict([('zhaobiao','1'),('zhongbiao','2')])

    listtypezfcg=OrderedDict([("zgys", "1"),("zhaobiao","2"),("kongzhijia", "3"), ("biangeng", "4"),
                            ("zgysjg", "5"),("zhongbiaohx","6"),("liubiao", "7"),('zhaobiao_tanpan','14'),
                            ('zhaobiao_cuoshang','8'),('zhaobiao_xunjia','9'),('zhaobiao_danyilaiyuan','11'),('zhaobiao_jinkou','24'),('zhaobiao_xieyi','10')])

    prozw_dict_zfcg=OrderedDict([("zhaobiao_jinkou","进口产品"),("zhaobiao_tanpan", "竞争性谈判"), ("zhaobiao_cuoshang", "竞争性磋商"),
                                 ("zhaobiao_xunjia","询价采购"),('zhaobiao_danyilaiyuan','单一性来源'),('zhaobiao_xieyi','协议供货')])


    ##新系统

    # ##fangjian_shizheng_jiaotong_shuili
    for ppt in pro_list[:4]:
        for llt in listtype.keys():
            href = "http://www.plsggzyjy.cn/f/newtrade/annogoods/getAnnoList?lch?listType={lt}?lch?projectType={pt}?lch?tradeStatus=0".format(lt=listtype[llt],pt=projecttype[ppt])
            tmp = ["gcjs_%s_%s_gg" % (llt, ppt), href, ["name","ggstart_time","href",'info'],
                   add_info(f1, {"gclx": prozw_dict[ppt]}), f2]
            data.append(tmp)
    #
    # ##zfcg
    for ppt in pro_list[4:5]:
        for llt in listtypezfcg.keys():
            href = "http://www.plsggzyjy.cn/f/newtrade/annogoods/getAnnoList?lch?listType={lt}?lch?projectType={pt}?lch?tradeStatus=0".format(
                lt=listtypezfcg[llt], pt=projecttype[ppt])

            tmp = ["zfcg_%s_gg" % (llt), href, ["name", "ggstart_time", "href", 'info'],

                   add_info(f1, {"zbfs": prozw_dict_zfcg[llt]}) if 'zhaobiao_' in llt else f1, f2]
            data.append(tmp)

    #xiane
    for ppt in pro_list[-2:]:
        for llt in listtype_xiane:
            href = "http://www.plsggzyjy.cn/f/purchase/purchaseAnnoment/getAnnoList?type={gc}&tabType={lt}&annomentTitle=?lch?listType={lt}?lch?projectType={pt}?lch?tradeStatus=0".format(gc=gc_dict[ppt],lt=listtype_xiane[llt],pt=projecttype[ppt])
            tmp = ["%s_%s_gg" % (ppt,llt), href, ["name","ggstart_time","href",'info'],
                   add_info(f1, {"gclx": prozw_dict[ppt]}), f2]
            data.append(tmp)


    ##旧系统

    ##fangjian_shizheng_jiaotong_shuili
    for ppt in pro_list[:4]:
        for llt in listtype.keys():
            href = "http://www.plsggzyjy.cn/f/newtrade/annogoods/getAnnoList?lch?listType={lt}?lch?projectType={pt}?lch?tradeStatus=1".format(lt=listtype[llt],pt=projecttype_old[ppt])
            tmp = ["gcjs_%s_%s_old_gg" % (llt, ppt), href, ["name","ggstart_time","href",'info'],
                   add_info(f1, {"gclx": prozw_dict[ppt]}), f2]
            data.append(tmp)


    ##zfcg
    for ppt in pro_list[4:5]:
        for llt in listtypezfcg.keys():
            href = "http://www.plsggzyjy.cn/f/newtrade/annogoods/getAnnoList?lch?listType={lt}?lch?projectType={pt}?lch?tradeStatus=1".format(
                lt=listtypezfcg[llt], pt=projecttype_old[ppt])

            tmp = ["zfcg_%s_old_gg" % (llt), href, ["name", "ggstart_time", "href", 'info'],

                   add_info(f1, {"zbfs": prozw_dict_zfcg[llt]}) if 'zhaobiao_' in llt else f1, f2]
            data.append(tmp)

    remove_arr = ["zfcg_zhaobiao_xieyi_old_gg","zfcg_zhaobiao_jinkou_old_gg"]

    data1 = data.copy()
    for w in data:
        if w[0] in remove_arr: data1.remove(w)


    return data1


data=get_data()
# pprint(data)


### url='http://www.plsggzyjy.cn/f/newtrade/annogoods/list'


## f3 为全流程


def work(conp,**args):
    est_meta(conp,data=data,diqu="甘肃省平凉市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    # work(conp=["postgres","since2015",'192.168.3.171',"gansu","pingliang"])
    pass
    driver=webdriver.Chrome()
    url='http://www.plsggzyjy.cn/f/purchase/purchaseAnnoment/getAnnoList?type=engineer&tabType=1&annomentTitle=?lch?listType=1?lch?projectType=11?lch?tradeStatus=0'
    driver.get(url)
    q=f1(driver,num=1)
    print(q)