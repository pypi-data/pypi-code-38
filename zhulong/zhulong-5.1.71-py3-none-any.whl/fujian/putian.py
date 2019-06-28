from collections import OrderedDict
from os.path import join, dirname

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
from zhulong.util.etl import add_info, est_meta, est_html, est_tbs, gg_existed
from zhulong.util.conf import get_conp
_name_="putian"


def f1(driver, num):
    url = driver.current_url
    locator = (By.XPATH, "//ul[@class='ewb-notice-items']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//td[@class='huifont']")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = re.findall(r'(\d+)/', st)[0]
    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='ewb-notice-items']/li[1]/a").get_attribute('href')[-30:]
        if "?Paging" not in url:
            s = "?Paging=%d" % (num) if num > 1 else "?Paging=1"
            url = url + s
        elif num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
        driver.get(url)
        locator = (By.XPATH, "//ul[@class='ewb-notice-items']/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("ul", class_="ewb-notice-items")
    trs = table.find_all("li", class_="clearfix")
    data = []
    for tr in trs:
        a = tr.find('a')
        try:
            title = a["title"].strip()
        except:
            title = a.text.strip()

        href = a["href"].strip()
        if 'http' in href:
            link = href
        else:
            link = "http://ggzyjy.ptfwzx.gov.cn" + href
        td = tr.find("span", class_="r ewb-date").text.strip()
        tmp = [title, td, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df



def f2(driver):
    # url = driver.current_url
    if ('本栏目暂时没有内容' in driver.page_source) or ('404' in driver.title):
        return 0
    locator = (By.XPATH, "//ul[@class='ewb-notice-items']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//td[@class='huifont']")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'/(\d+)', st)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    if ('无法访问此网站' in driver.page_source) or ('404' in driver.title):
        return 404
    locator = (By.XPATH, "//table[@id='tblInfo'][string-length()>200]")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    locator = (By.XPATH, "//td[@id='TDContent'][string-length()>200]")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    before = len(driver.page_source)
    time.sleep(0.5)
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
    div = soup.find('table', id="tblInfo")
    return div



def get_data():
    data = []
    # 工程建设部分
    xs = OrderedDict([("市中心", "002"),("仙游县", "003"), ("荔城区", "004"), ("城厢区", "005"), ("涵江区", "006"),
                      ("秀屿区", "007"), ("北岸经济开发区", "008"), ("湄洲岛", "009")])
    ggtype = OrderedDict([("zhaobiao", "005"),("gqita_zhong_liu", "010")])

    for w1 in ggtype.keys():
        for w2 in xs.keys():
            p1 = "004002%s" % (ggtype[w1])
            p2 = "004002%s%s" % (ggtype[w1], xs[w2])
            href = "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004002/%s/%s/" % (p1, p2)

            tb = "gcjs_%s_diqu%s_gg" % (w1, xs[w2])
            col = ["name", "ggstart_time", "href", "info"]
            tmp = [tb, href, col, add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)

    # 政府采购部分
    lx = OrderedDict([("办公设备", "001"), ("电器设备", "002"), ("网络设备", "003"), ("交通工具", "004"), ("医疗机械", "005"),
                      ("家具", "006"), ("其他", "007")])
    ggtype2 = OrderedDict([("zhaobiao", "005")])
    ggtype3 = OrderedDict([("gqita_zhong_liu", "005")])

    for w1 in ggtype2.keys():
        for w2 in lx.keys():
            p1 = "004003002%s" % (ggtype2[w1])
            p2 = "004003002%s%s" % (ggtype2[w1], lx[w2])
            href = "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003002/%s/%s/" % (p1, p2)

            tb = "zfcg_%s_diqu%s_gg" % (w1, lx[w2])
            col = ["name", "ggstart_time", "href", "info"]
            tmp = [tb, href, col, add_info(f1, {"leixing": w2}), f2]
            data.append(tmp)

    for w1 in ggtype3.keys():
        for w2 in lx.keys():
            p1 = "004003006%s" % (ggtype3[w1])
            p2 = "004003006%s%s" % (ggtype3[w1], lx[w2])
            href = "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003006/%s/%s/" % (p1, p2)
            tb = "zfcg_%s_diqu%s_gg" % (w1, lx[w2])
            col = ["name", "ggstart_time", "href", "info"]
            tmp = [tb, href, col, add_info(f1, {"leixing": w2}), f2]
            data.append(tmp)

    data1 = data.copy()
    remove_arr = []
    for w in data:
        if w[0] in remove_arr: data1.remove(w)
    return data1
    # 创建data

data1 = get_data()


data2 = [
    ["gcjs_kongzhijia_gg",
     "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004002/004002006/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004002/004002007/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004002/004002022/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_biangeng_sheji_gg",
     "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004002/004002008/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"gctype":"设计"}), f2],

    ["gcjs_kaibiao_gg",
     "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004002/004002023/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003002/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_yaoqing_gg",
     "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003002/004003002006/004003002006007/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':"邀请招标"}), f2],

    ["zfcg_zhaobiao_jingzheng_gg",
     "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003002/004003002007/004003002007007/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':"竞争性谈判"}), f2],

    ["zfcg_zhaobiao_yijia1_gg",
     "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003002/004003002002/004003002002001/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"zbfs":"竞争性谈判","chanping":"办公设备"}), f2],

    ["zfcg_zhaobiao_yijia2_gg",
     "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003002/004003002002/004003002002004/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{"zbfs":"竞争性谈判","chanping":"交通工具"}), f2],

    ["zfcg_zhaobiao_xunjia_gg",
     "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003002/004003002004/004003002004007/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"zbfs":"询价"}), f2],

    ["zfcg_zhaobiao_danyilaiyuan_gg",
     "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003002/004003002008/004003002008007/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"zbfs":"单一来源"}), f2],

    ["zfcg_gqita_zhong_liu_gg",
     "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003006/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_zhong_liu_yaoqing1_gg",
     "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003006/004003006006/004003006006004/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"zbfs":"邀请招标"}), f2],

    ["zfcg_gqita_zhong_liu_yaoqing2_gg",
     "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003006/004003006006/004003006006007/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"zbfs":"邀请招标"}), f2],

    ["zfcg_gqita_zhong_liu_jingzheng_gg",
     "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003006/004003006007/004003006007007/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"zbfs":"竞争谈判"}), f2],

    ["zfcg_gqita_zhong_liu_yijia_gg",
     "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003006/004003006002/004003006002004/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"zbfs":"议价"}), f2],

    ["zfcg_gqita_zhong_liu_xunjia_gg",
     "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003006/004003006004/004003006004007/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"zbfs":"询价"}), f2],

    ["zfcg_gqita_zhong_liu_danyilaiyuan_gg",
     "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003006/004003006008/004003006008007/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"zbfs":"单一来源"}), f2],

    ["zfcg_zgys_gg",
     "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003015/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_bian_da_gg",
     "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003003/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://ggzyjy.ptfwzx.gov.cn/fwzx/wjzyzx/004003/004003004/",
    ["name", "ggstart_time", "href", "info"],f1,f2],

]

data = data1 + data2



def work(conp,**args):
    est_meta(conp,data=data,diqu="福建省莆田市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","fujian","putian"],pageloadtimeout=180, pageloadstrategy="none", num=1, headless=False)


# 修改日期：2019/5/27
# 新网址：http://ggzyjy.ptfwzx.gov.cn/fwzx/

