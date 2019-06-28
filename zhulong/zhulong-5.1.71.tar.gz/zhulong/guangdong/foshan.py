import json

from collections import OrderedDict
from pprint import pprint

import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write, db_command, db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, add_info, est_gg

# driver=webdriver.Chrome()
# url="http://www.bygzjy.cn/f/trade/annogoods/list?selectedProjectType=3"
# driver.get(url)

_name_ = 'foshan'


def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]//a')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    url = driver.current_url

    if 'ddcgzq_1108567' in url:
        if re.findall('index.html', url):
            cnum = 1
        else:
            cnum = int(re.findall('index_(\d+).html', url)[0])
    else:

        if re.findall('index_\d+.html',url):
            cnum = 1
        else:
            cnum = int(re.findall('index_\d+_(\d+).html', url)[0])

    if cnum != num:
        val = driver.find_element_by_xpath(
            '//ul[@class="wb-data-item"]/li[1]//a').get_attribute('href')[-25:-5]

        if 'ddcgzq_1108567' in url:
            url = re.sub('index_{0,1}\d*.html', 'index_%s.html' % num, url) if num != 1 else \
                re.sub('index_{0,1}\d*.html', 'index.html', url)
        else:

            mark_url=re.findall('index_(\d+)_{0,1}\d*.html',url)[0]

            url = re.sub('index_\d+_{0,1}\d*.html','index_%s_%s.html'%(mark_url,num),url) if num != 1 else\
                re.sub('index_\d+_{0,1}\d*.html','index_%s.html'%mark_url, url)

        driver.get(url)
        # print(url)

        locator = (
            By.XPATH, "//ul[@class='wb-data-item']/li[1]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("ul", class_="wb-data-item")
    dls = div.find_all("li", recursive=False)

    data = []
    for dl in dls:

        name = dl.find('a')['title']
        href = dl.find('a')['href'].strip('.')
        ggstart_time = dl.find('span', class_='wb-data-date').get_text()

        if 'http' in href:
            href = href
        else:
            href = url.rsplit('/',maxsplit=1)[0] + href

        tmp = [name, ggstart_time, href]
        # print(tmp)
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None

    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]//a')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    html = driver.page_source
    total = re.findall('createPageHTML\((\d+), ', html)[0]

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="ewb-article-info"][string-length()>50]')
    WebDriverWait(
        driver, 10).until(
        EC.presence_of_all_elements_located(locator))

    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 5:
            break

    # f3 情况1
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_='ewb-article')

    return div


data2 = [

    ["zfcg_zhaobiao_huowu_gg",
     "http://www.fsggzy.cn/jyxx/fss/zfcg_1108551/ddcgzq_1108567/hwlddcgml/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"zbfs":"货物定点采购"}), f2],

    ["zfcg_zhaobiao_fuwu_gg",
     "http://www.fsggzy.cn/jyxx/fss/zfcg_1108551/ddcgzq_1108567/hwlddcgml/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"zbfs":"服务定点采购"}), f2],

    ["zfcg_zhaobiao_gongcheng_gg",
     "http://www.fsggzy.cn/jyxx/fss/zfcg_1108551/ddcgzq_1108567/hwlddcgml/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"zbfs":"工程定点采购"}), f2],

]



def get_data():
    data = []



    #gcjs
    ggtype1 = OrderedDict([("zhaobiao","zbgg/index_28799"),("zhongbiaohx", "pbgs/index_28799"), ("zhongbiao", "zbjggk/index_29108")])
    #zfcg
    ggtype2 = OrderedDict([("zhaobiao","cggg/index_28799"),("yucai", "cgyjzj/index_29108"),
                           ("biangeng", "gzgg/index_29108"),("zhongbiao", "zbxx/index_29108")])
    #yiliao
    ggtype3 = OrderedDict([("zhaobiao","cggg_1108571/index_28799"),("yucai", "cgyjzjx/index_29108"),
                           ("biangeng", "gzgg_1108574/index_29108"),("zhongbiaohx", "jggg/index_29108")])

    #qsy
    ggtype4 = OrderedDict([("zhaobiao", "cggg_1108577/index_28799"), ("yucai", "xqyjzjuu/index_28799"),
                           ("biangeng", "gzgg_1108580/index_29108"), ("zhongbiaohx", "jggs_1108578/index_29108"),
                           ("zhongbiao", "jggg_1108579/index_29108")])

    ##jqita_daili   jqita
    ggtype5=OrderedDict([("zhaobiao", "jyggx1/index_28799"), ("zhongbiao", "jyjgx1/index_28799"),
                           ("gqita", "qtxxx1/index_28799")])



    adtype1 = OrderedDict([('佛山市','fss'),("禅城区", "ccq"), ("南海区", "nhq"),
                           ("顺德区","sdq"),("三水区","ssq"),('高明区', 'gmq')])



    #gcjs
    for w1 in ggtype1.keys():
        for w2 in adtype1.keys():
            href = "http://www.fsggzy.cn/jyxx/{dq}/gcjy_1108550/{jy}.html".format(dq=adtype1[w2],jy=ggtype1[w1])
            tmp = ["gcjs_%s_%s_gg" % (w1, adtype1[w2]), href, ["name","ggstart_time","href",'info'],
                   add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)

    # zfcg
    for w1 in ggtype2.keys():
        for w2 in adtype1.keys():
            href = "http://www.fsggzy.cn/jyxx/{dq}/zfcg_1108551/{jy}.html".format(dq=adtype1[w2], jy=ggtype2[w1])
            tmp = ["zfcg_%s_%s_gg" % (w1, adtype1[w2]), href, ["name", "ggstart_time", "href", 'info'],
                   add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)
    # yiliao
    for w1 in ggtype3.keys():
        href = "http://www.fsggzy.cn/jyxx/fss/yxcg/{jy}.html".format( jy=ggtype3[w1])
        tmp = ["yiliao_%s_fss_gg" % (w1), href, ["name", "ggstart_time", "href", 'info'],
               add_info(f1, {"diqu": '佛山市'}), f2]
        data.append(tmp)

    # jqita
    for w1 in ggtype5.keys():
        href = "http://www.fsggzy.cn/jyxx/fss/qt0001/{jy}.html".format(jy=ggtype5[w1])
        tmp = ["jqita_%s_fss_gg" % (w1), href, ["name", "ggstart_time", "href", 'info'],
               add_info(f1, {"diqu": '佛山市'}), f2]
        data.append(tmp)

    # jqita_daili
    for w1 in ggtype5.keys():
        href = "http://www.fsggzy.cn/jyxx/fss/shdl18081103/{jy}.html".format(jy=ggtype5[w1])
        tmp = ["jqita_daili_%s_fss_gg" % (w1), href, ["name", "ggstart_time", "href", 'info'],
               add_info(f1, {"diqu": '佛山市','gclx':"社会代理采购业务"}), f2]
        data.append(tmp)

    # qsy
    for w1 in ggtype4.keys():

        href = "http://www.fsggzy.cn/jyxx/fss/qycg_1108553/{jy}.html".format( jy=ggtype4[w1])
        tmp = ["qsy_%s_fss_gg" % (w1), href, ["name", "ggstart_time", "href", 'info'],
               add_info(f1, {"diqu": "佛山市"}), f2]
        data.append(tmp)


    data1 = data.copy()
    data1.extend(data2)
    return data1


data=get_data()




##招标答疑 要登录 ,未爬取

def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省佛山市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(
        conp=[
            "postgres",
            "since2015",
            '192.168.3.171',
            "guangdong",
            "foshan"],
        headless=False,
        num=1,
        total=3)
    pass