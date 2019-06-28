from collections import OrderedDict
from os.path import dirname, join
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
from zhulong.util.conf import get_conp
from zhulong.util.etl import add_info, est_meta, est_html, est_tbs, gg_existed

_name_="lishui"


def f1(driver, num):
    locator = (By.XPATH, "(//tr[@height='25']/td/a)[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//td[@class='huifont']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        cnum = re.findall(r'(\d+)/', str)[0]
    except:
        cnum = 1
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("(//tr[@height='25']/td/a)[1]").get_attribute('href')[-45:]
        if "Paging" not in url:
            s = "?Paging=%d" % (num) if num > 1 else "?Paging=1"
            url = url + s
        elif num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
        driver.get(url)
        locator = (By.XPATH, "(//tr[@height='25']/td/a)[1][not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", cellspacing='3')
    trs = table.find_all("tr", height="25")
    data = []
    for tr in trs:
        a = tr.find("a")
        try:
            title = a["title"].strip()
        except:
            title = a.text.strip()
        td = tr.find("font", color="#000000").text.strip()
        link = "http://www.lssggzy.com" + a["href"].strip()
        tmp = [title, td, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df



def f2(driver):
    if ("本栏目暂时没有内容" in driver.page_source) or ('404' in driver.title):
        return 0
    locator = (By.XPATH, "(//tr[@height='25']/td/a)[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//td[@class='huifont']")
        st = WebDriverWait(driver, 5).until(EC.presence_of_element_located(locator)).text
        num = int(re.findall(r'/(\d+)', st)[0])
    except:
        num = 1
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    if '404' in driver.title:
        return 404
    locator = (By.XPATH, "//table[@style='overflow:hidden']")
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
    div = soup.find('table', style="overflow:hidden")
    div = div.find_all('tr')
    return div


def get_data():
    xs=OrderedDict([("市级","001"),("莲都","002"),("龙泉","003"),("青田","004"),("云和","005")
        ,("庆元","006"),("缙云","007"),("遂昌","008"),("松阳","009"),("景宁","010")])
    ##工程建设
    ggtype1=OrderedDict([("zhaobiao","001"),("gqita_bian_bu","002"),("kaibiao","003"),("zhongbiaohx","004"),("zhongbiao","005")])

    ggtype2=OrderedDict([("zhaobiao","001"),("gqita_bian_bu","002"),("zhongbiao","003")])

    data=[]
    for w1 in ggtype1.keys():
        for w2 in xs.keys():
            p1="071001%s"%(ggtype1[w1])
            p2="071001%s%s"%(ggtype1[w1],xs[w2])
            href="http://www.lssggzy.com/lsweb/jyxx/071001/%s/%s/?Paging=1"%(p1,p2)
            tmp=["gcjs_%s_diqu%s_gg"%(w1,xs[w2]),href,["name","ggstart_time","href","info"],add_info(f1,{"diqu":w2}),f2]
            data.append(tmp)

    for w1 in ggtype2.keys():
        for w2 in xs.keys():
            p1="071001006%s"%(ggtype2[w1])
            p2="071001006%s%s"%(ggtype2[w1],xs[w2])
            href="http://www.lssggzy.com/lsweb/jyxx/071001/071001006/%s/%s/?Paging=1"%(p1,p2)
            tmp=["gcjs_%s_diqu%s_xiaoer_gg"%(w1,xs[w2]),href,["name","ggstart_time","href","info"],add_info(f1,{"diqu":w2, 'xmlx':'小额项目'}),f2]
            data.append(tmp)

    ## 政府采购
    ggtype3=OrderedDict([("zhaobiao","002"),("biangeng","003"),("zhongbiaohx","007"),("zhongbiao","005"),("hetong","006"),("yucai","001")])
    for w1 in ggtype3.keys():
        for w2 in xs.keys():
            p1="071002%s"%(ggtype3[w1])
            p2="071002%s%s"%(ggtype3[w1],xs[w2])
            href="http://www.lssggzy.com/lsweb/jyxx/071002/%s/%s/?Paging=1"%(p1,p2)
            tmp=["zfcg_%s_diqu%s_gg"%(w1,xs[w2]),href,["name","ggstart_time","href","info"],add_info(f1,{"diqu":w2}),f2]
            data.append(tmp)

    ## 其他交易
    ggtype4 = OrderedDict([("zhaobiao", "001"), ("gqita_bian_bu", "002"), ("zhongbiao", "003")])
    for w1 in ggtype4.keys():
        for w2 in xs.keys():
            p1="071005%s"%(ggtype4[w1])
            p2="071005%s%s"%(ggtype4[w1],xs[w2])
            href="http://www.lssggzy.com/lsweb/jyxx/071005/%s/%s/?Paging=1"%(p1,p2)
            tmp=["qsy_%s_diqu%s_gg"%(w1,xs[w2]),href,["name","ggstart_time","href","info"],add_info(f1,{"diqu":w2,'jylx':'其他交易'}),f2]
            data.append(tmp)


    data1=data.copy()
    arr=[]
    for w in data:
        if w[0] in arr:data1.remove(w)
    return data1

data1=get_data()


data2 = [
    ["zfcg_zhaobiao_xieyi_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071002/071002008/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'协议'}), f2],

    ["zfcg_zhongbiao_xieyi_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071002/071002009/",
     ["name", "ggstart_time", "href", "info"],  add_info(f1, {'zbfs':'协议'}), f2],

    ["zfcg_liubiao_zhongzhi_gg",
     "http://www.lssggzy.com/lsweb/jyxx/071002/071002011/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]

data = data1+data2


def work(conp,**args):
    est_meta(conp,data=data,diqu="浙江省丽水市",**args)
    est_html(conp,f=f3,**args)

# 修改日期：2019/6/28
if __name__=='__main__':
    work(conp=["postgres","zhulong.com.cn","192.168.169.47","zhejiang","lishui"],pageloadtimeout=120)


