import time
from collections import OrderedDict
from pprint import pprint

import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zhulong.util.etl import est_tables, gg_html, gg_meta, add_info, est_meta, est_html

_name_="dezhou"


def f1(driver, num):
    """
    进行翻页，并获取数据
    :param driver: 已经访问了url
    :param num: 返回的是从第一页一直到最后一页
    :return:
    """
    locator = (By.XPATH, '//table[@cellspacing="3"]/tbody/tr[1]/td[2]/a | //ul[@class="ewb-list"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        locator = (By.XPATH, '//td[@class="huifont"] | //a[@class="wb-page-default wb-page-number wb-page-family"]')
        page_all = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        cnum = int(re.findall('(\d+)/', page_all)[0])
    except:
        cnum = 1
    try:
        flag = 1
        val = driver.find_element_by_xpath('//table[@cellspacing="3"]/tbody/tr[1]/td[2]/a').get_attribute('href')[-45:]
    except:
        flag = 2
        val_1 = driver.find_element_by_xpath('//ul[@class="ewb-list"]/li[1]/a').get_attribute('href')[-45:]
    if num != int(cnum):
        if 'Paging' not in url:
            s = "?Paging=%d" % (num) if num > 1 else "?Paging=1"
            url += s
        elif num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
        driver.get(url)
        locator = (By.XPATH, '//td[@class="huifont"] | //a[@class="wb-page-default wb-page-number wb-page-family"]')
        page_all = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        page = re.findall('(\d+)/', page_all)[0]
        if int(page) != num:
            raise TimeoutError
        if flag == 1:
            locator = (By.XPATH, "//table[@cellspacing='3']/tbody/tr[1]/td[2]/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        if flag == 2:
            locator = (By.XPATH, "//ul[@class='ewb-list']/li[1]/a[not(contains(@href, '%s'))]" % val_1)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    if flag == 1:
        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        ul = soup.find("div", class_="ewb-right-info")
        tb = ul.find_all("div", recursive=False)[0]
        lis = tb.find_all("tr")
        data = []
        for li in lis:
            a = li.find("a")
            try:
                title = a["title"]
            except:
                title = a.text.strip()
            link = "http://ggzyjy.dezhou.gov.cn" + a["href"]
            span = li.find_all("font")[-1]
            tmp = [title, span.text.strip(), link]
            data.append(tmp)
        df = pd.DataFrame(data=data)
        df["info"]=None
        return df
    if flag == 2:
        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        ul = soup.find("ul", class_="ewb-list")
        lis = ul.find_all("li")
        data = []
        for li in lis:
            a = li.find("a")
            try:
                title = a["title"]
            except:
                title = a.text.strip()
            link = "http://ggzyjy.dezhou.gov.cn" + a["href"]
            span = li.find("span", class_='ewb-list-date').text.strip()
            tmp = [title, span, link]
            data.append(tmp)
        df = pd.DataFrame(data=data)
        df["info"]=None
        return df

def f2(driver):
    """
    返回总页数
    :param driver:
    :return:
    """
    locator = (By.XPATH, '//table[@cellspacing="3"]/tbody/tr[1]/td[2]/a | //ul[@class="ewb-list"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, '//td[@class="huifont"] | //a[@class="wb-page-default wb-page-number wb-page-family"]')
        page_all = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        page = re.findall('/(\d+)', page_all)[0]
    except:
        page = 1
    driver.quit()
    return int(page)



def f3(driver,url):
    driver.get(url)
    time.sleep(1)
    locator=(By.XPATH, "//div[contains(@id,'menutab')][string-length()>30] | //div[@class='ewb-right-info'][string-length()>30]")
    WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))
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
    if 'ewb-right-info' in page:
        div=soup.find('div',class_='ewb-right-info')
    else:
        div=soup.find("div",id=re.compile("menutab.*"),style='')
    return div


data1 = [
    ["gcjs_yucai_gg", "http://ggzyjy.dezhou.gov.cn/TPFront/xmxx/004001/004001005/004001005001/?Paging=1",
     ["name", "ggstart_time", "href","info"],add_info(f1,{'diqu':'市本级'}),f2],

    ["gcjs_zhaobiao_gg", "http://ggzyjy.dezhou.gov.cn/TPFront/xmxx/004001/004001001/004001001001/?Paging=1",
     ["name", "ggstart_time", "href","info"],add_info(f1,{'diqu':'市本级'}),f2],

    ["gcjs_biangeng_gg", "http://ggzyjy.dezhou.gov.cn/TPFront/xmxx/004001/004001002/004001002001/?Paging=1",
     ["name", "ggstart_time", "href","info"],add_info(f1,{'diqu':'市本级'}),f2],

    ["gcjs_zhongbiaohx_gg", "http://ggzyjy.dezhou.gov.cn/TPFront/xmxx/004001/004001008/004001008001/?Paging=1",
     ["name", "ggstart_time", "href","info"],add_info(f1,{'diqu':'市本级'}),f2],

    ["gcjs_gqita_zhong_liu_gg", "http://ggzyjy.dezhou.gov.cn/TPFront/xmxx/004001/004001003/004001003001/?Paging=1",
     ["name", "ggstart_time", "href","info"],add_info(f1,{'diqu':'市本级'}),f2],

    ["gcjs_hetong_gg", "http://ggzyjy.dezhou.gov.cn/TPFront/xmxx/004001/004001006/004001006001/?Paging=1",
     ["name", "ggstart_time", "href","info"],add_info(f1,{'diqu':'市本级'}),f2],

    ["zfcg_zhaobiao_gg", "http://ggzyjy.dezhou.gov.cn/TPFront/xmxx/004002/004002001/004002001001/?Paging=1",
     ["name", "ggstart_time", "href","info"],add_info(f1,{'diqu':'市本级'}),f2],

    ["zfcg_biangeng_gg", "http://ggzyjy.dezhou.gov.cn/TPFront/xmxx/004002/004002002/004002002001/?Paging=1",
     ["name", "ggstart_time", "href","info"],add_info(f1,{'diqu':'市本级'}),f2],

    ["zfcg_gqita_zhong_liu_gg", "http://ggzyjy.dezhou.gov.cn/TPFront/xmxx/004002/004002003/004002003001/?Paging=1",
     ["name", "ggstart_time", "href","info"],add_info(f1,{'diqu':'市本级'}),f2],

    ["zfcg_yucai_gg", "http://ggzyjy.dezhou.gov.cn/TPFront/xmxx/004002/004002005/004002005001/?Paging=1",
     ["name", "ggstart_time", "href","info"],add_info(f1,{'diqu':'市本级'}),f2],

    ["zfcg_hetong_gg", "http://ggzyjy.dezhou.gov.cn/TPFront/xmxx/004002/004002006/004002006001/?Paging=1",
     ["name", "ggstart_time", "href","info"],add_info(f1,{'diqu':'市本级'}),f2],

    ["qsy_yucai_gg", "http://ggzyjy.dezhou.gov.cn/TPFront/xmxx/004006/004006002/004006002001/004006002001001/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'货物服务','diqu':'市本级'}), f2],

    ["qsy_zhaobiao_gg", "http://ggzyjy.dezhou.gov.cn/TPFront/xmxx/004006/004006002/004006002002/004006002002001/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'货物服务','diqu':'市本级'}), f2],

    ["qsy_biangeng_gg",
     "http://ggzyjy.dezhou.gov.cn/TPFront/xmxx/004006/004006002/004006002003/004006002003001/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'货物服务','diqu':'市本级'}), f2],

    ["qsy_gqita_zhong_liu_gg",
     "http://ggzyjy.dezhou.gov.cn/TPFront/xmxx/004006/004006002/004006002004/004006002004001/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'货物服务','diqu':'市本级'}), f2],

    ["qsy_hetong_gg",
     "http://ggzyjy.dezhou.gov.cn/TPFront/xmxx/004006/004006002/004006002005/004006002005001/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'货物服务','diqu':'市本级'}), f2],

]



def get_data():
    data = []
    # 工程建设部分
    xs1 = OrderedDict([("陵城区", "lc"), ("禹城市", "yc"), ("乐陵市", "ll"), ("宁津县", "nj"), ("齐河县", "qh"),
                      ("临邑县", "ly"), ("平原县", "py"), ("武城县", "wc"), ("夏津县", "xj"), ("庆云县", "qy")])

    xs2 = OrderedDict([("陵城区", "004"), ("禹城市", "003"), ("乐陵市", "002"), ("宁津县", "005"), ("齐河县", "006"),
                      ("临邑县", "007"), ("平原县", "008"), ("武城县", "009"), ("夏津县", "011"), ("庆云县", "010")])
    # # "http://ggzyjy.dezhou.gov.cn/ll/xmxx/004001/004001005/004001005002/?Paging=1"
    ggtype = OrderedDict([("zhaobiao", "001"), ("biangeng", "002"), ("zhongbiao", "003"), ("yucai", "005"), ("hetong", "006")])
    ggtype1 = OrderedDict([("zhaobiao", "001"), ("biangeng", "002"), ("zhongbiao", "003"), ("zhongbiaohx", "008")])
    ggtype2 = OrderedDict([("zhaobiao", "001"), ("biangeng", "002"), ("zhongbiao", "003"), ("zgysjg", "005"), ("hetong","006"), ("yucai", "007")])
    for w1 in xs1.keys():
        if w1 == "宁津县":
            for w2 in ggtype1.keys():
                for w3 in xs2.keys():
                    if w1 == w3:
                        p1 = "004001%s" % (ggtype1[w2])
                        p2 = "004001%s%s" % (ggtype1[w2], xs2[w3])
                        href = "http://ggzyjy.dezhou.gov.cn/%s/xmxx/004001/%s/%s/?Paging=1" % (xs1[w1], p1, p2)
                        tb = "gcjs_%s_diqu%s_gg" % (w2, xs2[w3])
                        col = ["name", "ggstart_time", "href", "info"]
                        tmp = [tb, href, col, add_info(f1, {"diqu": w3}), f2]
                        data.append(tmp)
        elif w1 == "齐河县":
            for w2 in ggtype2.keys():
                for w3 in xs2.keys():
                    if w1 == w3:
                        p1 = "004001%s" % (ggtype2[w2])
                        p2 = "004001%s%s" % (ggtype2[w2], xs2[w3])
                        if w2 == 'yucai':
                            href = "http://ggzyjy.dezhou.gov.cn/qh/xmxx/004001/004001007/004001007001/?Paging=1"
                        else:
                            href = "http://ggzyjy.dezhou.gov.cn/%s/xmxx/004001/%s/%s/?Paging=1" % (xs1[w1], p1, p2)
                        tb = "gcjs_%s_diqu%s_gg" % (w2, xs2[w3])
                        col = ["name", "ggstart_time", "href", "info"]
                        tmp = [tb, href, col, add_info(f1, {"diqu": w3}), f2]
                        data.append(tmp)
        else:
            for w2 in ggtype.keys():
                for w3 in xs2.keys():
                    if w1 == w3:
                        p1 = "004001%s" % (ggtype[w2])
                        p2 = "004001%s%s" % (ggtype[w2], xs2[w3])
                        href = "http://ggzyjy.dezhou.gov.cn/%s/xmxx/004001/%s/%s/?Paging=1" % (xs1[w1], p1, p2)
                        tb = "gcjs_%s_diqu%s_gg" % (w2, xs2[w3])
                        col = ["name", "ggstart_time", "href", "info"]
                        tmp = [tb, href, col, add_info(f1, {"diqu": w3}), f2]
                        data.append(tmp)

    # 政府采购部分
    ggtype2 = OrderedDict([("zhaobiao", "001"), ("biangeng", "002"), ("gqita_zhong_liu", "003"),("yucai", "005"), ("hetong", "006")])
    # 'http://ggzyjy.dezhou.gov.cn/qy/xmxx/004002/004002001/004002001010/?Paging=3'
    for w1 in xs1.keys():
        for w2 in ggtype2.keys():
            for w3 in xs2.keys():
                if w1 == w3:
                    p1 = "004002%s" % (ggtype2[w2])
                    p2 = "004002%s%s" % (ggtype2[w2], xs2[w3])
                    href = "http://ggzyjy.dezhou.gov.cn/%s/xmxx/004002/%s/%s/?Paging=1" % (xs1[w1], p1, p2)
                    tmp = ['zfcg_%s_diqu%s_gg' % (w2, xs2[w3]), href,
                           ["name", "ggstart_time", "href", "info"], add_info(f1, {"diqu": w3}), f2]
                    data.append(tmp)

    data1 = data.copy()
    remove_arr = []
    for w in data:
        if w[0] in remove_arr: data1.remove(w)
    return data1
    # 创建data

data2 = get_data()

data = data1 + data2


def work(conp,**args):
    est_meta(conp,data=data,diqu="山东省德州市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shandong","dezhou"],pageloadtimeout=120,pageLoadStrategy="none")



# 修改时间：2019/5/23
# 域名修改：http://ggzyjy.dezhou.gov.cn/TPFront/


