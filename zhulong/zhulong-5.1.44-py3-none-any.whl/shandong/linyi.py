import time
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
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs
from collections import OrderedDict


_name_='linyi'


def f1(driver, num):
    locator = (By.XPATH, "(//ul[@class='ewb-news-items ewb-build-items']/li/a)[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cunn = driver.find_element_by_xpath('//span[@class="total-pages"]/strong').text
    cunm = re.findall('(\d+)/', cunn)[0]
    if num != int(cunm):
        if "?Paging" not in url:
            s = "?Paging=%d" % (num) if num > 1 else "?Paging=1"
            url+=s
        elif num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
        val = driver.find_element_by_xpath('(//ul[@class="ewb-news-items ewb-build-items"]/li/a)[1]').get_attribute('href')[-35:]
        driver.get(url)
        locator = (By.XPATH, "(//ul[@class='ewb-news-items ewb-build-items']/li/a)[1][not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    html_data = driver.page_source
    soup = BeautifulSoup(html_data, 'html.parser')
    ul = soup.find("ul", class_="ewb-news-items ewb-build-items")
    lis = ul.find_all("li")
    data = []
    for li in lis:
        a = li.find("a")
        title = a["title"]
        link = "http://ggzyjy.linyi.gov.cn" + a["href"]
        span = li.find("span")
        tmp = [title, span.text.strip(), link]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df



def f2(driver):
    """
    返回总页数
    :param driver:
    :return:
    """
    if ('本栏目信息正在更新中' in driver.page_source) or ('404' in driver.title):
        return 0
    locator = (By.XPATH, '//span[@class="total-pages"]/strong')
    page_all = WebDriverWait(driver, 1).until(EC.presence_of_element_located(locator)).text
    page = re.findall('/(\d+)', page_all)[0]
    total=int(page)

    driver.quit()
    return total

def f3(driver,url):
    driver.get(url)
    time.sleep(1)
    driver.switch_to_frame('navFrameContent')
    locator = (By.XPATH, "//body[not(@style)][string-length()>15]")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
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
    div=soup.find('body', style=False)
    return div


def get_data():
    data = []
    ggtype1 = OrderedDict([("zhaobiao", "001"), ("biangeng", "002"), ("zhongbiao", "003")])
    dwtype = OrderedDict(
        [("住建局", "001"), ("公路局", "002"), ("园林局", "003"), ("水利局", "004"), ("交通局", "005"), ("其它", "006")])
    # 工程建设
    for w1 in dwtype.keys():
        p1 = "074001001%s" % dwtype[w1]
        href = "http://ggzyjy.linyi.gov.cn/TPFront/jyxx/074001/074001001/%s/" % p1
        tmp = ["gcjs_zhaobiao_dw%s_gg" % dwtype[w1], href, ["name", "ggstart_time", "href", "info"],
               add_info(f1, {"dwtype": w1}), f2]
        data.append(tmp)

    tmp = ["gcjs_biangeng_gg", "http://ggzyjy.linyi.gov.cn/TPFront/jyxx/074001/074001002/",
           ["name", "ggstart_time", "href", "info"], f1, f2]
    data.append(tmp)
    dwtype1 = OrderedDict([("住建局", "001"), ("园林局", "003"),("交通局", "005"), ("其它", "006")])
    for w1 in dwtype1.keys():
        p1 = "074001003001%s" % dwtype1[w1]
        href = "http://ggzyjy.linyi.gov.cn/TPFront/jyxx/074001/074001003/074001003001/%s/" % p1
        tmp = ["gcjs_zgys_dw%s_gg" % dwtype1[w1], href, ["name", "ggstart_time", "href", "info"],
               add_info(f1, {"dwtype": w1}), f2]
        data.append(tmp)

    dwtype2 = OrderedDict([("住建局", "001"), ("公路局", "002"), ("水利局", "004"), ("交通局", "005"), ("其它", "006")])
    for w1 in dwtype2.keys():
        p1 = "074001003002%s" % dwtype2[w1]
        href = "http://ggzyjy.linyi.gov.cn/TPFront/jyxx/074001/074001003/074001003002/%s/" % p1
        tmp = ["gcjs_zhongbiaohx_dw%s_gg" % dwtype2[w1], href, ["name", "ggstart_time", "href", "info"],
               add_info(f1, {"dwtype": w1}), f2]
        data.append(tmp)

    dwtype3 = OrderedDict(
        [("住建局", "001"), ("公路局", "002"), ("园林局", "003"), ("水利局", "004"), ("交通局", "005"), ("其它", "006")])
    for w1 in dwtype3.keys():
        p1 = "074001003003%s" % dwtype3[w1]
        href = "http://ggzyjy.linyi.gov.cn/TPFront/jyxx/074001/074001003/074001003003/%s/" % p1
        tmp = ["gcjs_zhongbiao_dw%s_gg" % dwtype3[w1], href, ["name", "ggstart_time", "href", "info"],
               add_info(f1, {"dwtype": w1}), f2]
        data.append(tmp)

    # 政府采购
    ggtype = OrderedDict([("yucai", "001"), ("zhaobiao", "002"), ("zhongbiao", "004")])
    zbfs = OrderedDict(
        [("公开招标", "001"), ("竞争性谈判", "002"), ("邀请招标", "003"), ("单一来源", "004"), ("询价", "005"), ("协议采购", "006"),
         ("竞争性磋商", "007")])
    for w1 in ggtype.keys():
        for w2 in zbfs.keys():
            p1 = "074002%s" % ggtype[w1]
            p2 = "074002%s%s" % (ggtype[w1], zbfs[w2])
            href = "http://ggzyjy.linyi.gov.cn/TPFront/jyxx/074002/%s/%s/" % (p1,p2)
            tmp = ["zfcg_%s_zbfs%s_gg" % (w1, zbfs[w2]), href, ["name", "ggstart_time", "href", "info"],
                   add_info(f1, {"zbfs": w2}), f2]
            data.append(tmp)

    tmp = ["zfcg_biangeng_gg", "http://ggzyjy.linyi.gov.cn/TPFront/jyxx/074002/074002003/",
           ["name", "ggstart_time", "href", "info"], f1, f2]
    data.append(tmp)

    # 其他交易
    ggtype2 = OrderedDict([("zhaobiao", "001"), ("biangeng", "002"), ("zhongbiao", "003")])
    for w1 in ggtype2.keys():
        p1 = "074006%s" % ggtype2[w1]
        href = "http://ggzyjy.linyi.gov.cn/TPFront/jyxx/074006/%s/" % p1
        tmp = ["qsy_%s_gg" % w1, href, ["name", "ggstart_time", "href", "info"], add_info(f1,{'jylx':'其他交易'}), f2]
        data.append(tmp)
    data1 = data.copy()
    remove_arr = ["gcjs_zhongbiao_dw006_gg"]
    for w in data:
        if w[0] in remove_arr: data1.remove(w)
    return data1


data=get_data()


def work(conp,**args):
    est_meta(conp,data=data,diqu="山东省临沂市")
    est_html(conp,f=f3,**args)

if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shandong","linyi"])

