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

import json
from zhulong.util.etl import gg_meta, gg_html, est_html, est_meta, add_info

_name_ = "zhangjiajie"


# driver=webdriver.Chrome()

# url="""http://www.zjjsggzy.gov.cn/newsList.html?index=5&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xtype=%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE"""

# driver.get(url)


def f1(driver, num):
    locator = (By.XPATH, "//ul[@id='list']/li[2]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//div[@id='pageNav']//span[@class='cPageNum']")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = int(driver.find_element_by_xpath("//div[@id='pageNav']//span[@class='cPageNum']").text)
    if cnum != num:
        # val=driver.find_element_by_xpath("//ul[@id='list']/li[2]/a").text[-10:]
        driver.execute_script("javascript:pageNav.go(%d,);" % num)
        # locator=(By.XPATH,"//ul[@id='list']/li[2]//a[not(contains(string(),'%s'))]"%val)
        time.sleep(0.1)
        locator = (By.XPATH, "//div[@id='loading']")
        WebDriverWait(driver, 10).until(EC.invisibility_of_element(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    ul = soup.find("ul", id="list")
    lis = ul.find_all("li")[1:]
    data = []
    for li in lis:
        a = li.find("a")
        span = li.find("span")
        tmp = [a.text.strip(), "http://www.zjjsggzy.gov.cn" + a["href"], span.text.strip()]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, "//ul[@id='list']/li[2]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    text = driver.find_element_by_id("pageNav").get_attribute("title")
    total = re.findall("共([0-9]*)页", text)[0]
    total = int(total)
    driver.quit()
    return total


def switch_to(driver, xmtype, ggtype):
    locator = (By.ID, "list")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # cxmtype=driver.find_element_by_xpath("//ul[@class='rootNode']/li[@class='leafNode nodeselected']").text
    # if cxmtype!=xmtype:
    driver.find_element_by_xpath("//ul[@class='rootNode']/li[string()='%s']" % xmtype).click()
    time.sleep(0.1)
    locator = (By.XPATH, "//div[@id='loading']")
    WebDriverWait(driver, 10).until(EC.invisibility_of_element(locator))

    cggtype = driver.find_element_by_xpath("//div[@class='site-before']/button[@class='btn-site on']").text
    if cggtype != ggtype:
        driver.find_element_by_xpath("//div[@class='site-before']/button[string()='%s']" % ggtype).click()

        time.sleep(0.1)
        locator = (By.XPATH, "//div[@id='loading']")
        WebDriverWait(driver, 10).until(EC.invisibility_of_element(locator))


def gcjs(f, xmtype, ggtype):
    def wrap(*krg):
        driver = krg[0]
        switch_to(driver, xmtype, ggtype)
        if f == f1:
            df = f(*krg)
            a = {"xmtype": xmtype, "yuan_ggtype": ggtype}
            a = json.dumps(a, ensure_ascii=False)
            df["info"] = a
            return df
        else:
            return f(*krg)

    return wrap


def zfcg(f, xmtype, ggtype):
    def wrap(*krg):
        driver = krg[0]
        switch_to(driver, xmtype, ggtype)
        if f == f1:
            df = f(*krg)
            a = {"zbtype": xmtype, "yuan_ggtype": ggtype}
            a = json.dumps(a, ensure_ascii=False)
            df["info"] = a
            return df
        else:
            return f(*krg)

    return wrap


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//iframe[@id='myFrame']")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    page1 = driver.page_source
    soup1 = BeautifulSoup(page1, 'html.parser')
    div1 = soup1.find('div', class_='timeBanner')

    driver.switch_to.frame(driver.find_element_by_id("myFrame"))
    locator = (By.XPATH, "//div[@class='content'][string-length()>40]")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
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
    div2 = soup.find('div', class_='content')
    div = str(div1)+str(div2)
    return div


data = [
    # 房建市政
    ["gcjs_zhaobiao_fangwushizheng_gg",
     "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=0"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "房建市政", "招标公告"), gcjs(f2, "房建市政", "招标公告")],

    ["gcjs_gqita_bian_da_fangwushizheng_gg",
     "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=0"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "房建市政", "答疑/补充"), gcjs(f2, "房建市政", "答疑/补充")],

    ["gcjs_zhongbiaohx_fangwushizheng_gg",
     "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=0"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "房建市政", "中标候选人公示"), gcjs(f2, "房建市政", "中标候选人公示")],

    ["gcjs_zhongbiao_fangwushizheng_gg",
     "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=0"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "房建市政", "结果公示"), gcjs(f2, "房建市政", "结果公示")],

    # 交通运输工程
    ["gcjs_zhaobiao_jiaotong_gg",
     "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=0"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "交通运输工程", "招标公告"), gcjs(f2, "交通运输工程", "招标公告")],

    ["gcjs_zhongbiaohx_jiaotong_gg",
     "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=0"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "交通运输工程", "中标候选人公示"), gcjs(f2, "交通运输工程", "中标候选人公示")],

    ["gcjs_gqita_bian_da_jiaotong_gg",
     "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=0"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "交通运输工程", "答疑/补充"), gcjs(f2, "交通运输工程", "答疑/补充")],

    ["gcjs_zhongbiao_jiaotong_gg",
     "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=0"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "交通运输工程", "结果公示"), gcjs(f2, "交通运输工程", "结果公示")],

    # 水利工程
    ["gcjs_zhaobiao_shuili_gg",
     "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=0"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "水利工程", "招标公告"), gcjs(f2, "水利工程", "招标公告")],

    ["gcjs_zhongbiaohx_shuili_gg",
     "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=0"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "水利工程", "中标候选人公示"), gcjs(f2, "水利工程", "中标候选人公示")],

    ["gcjs_gqita_bian_da_shuili_gg",
     "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=0"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "水利工程", "答疑/补充"), gcjs(f2, "水利工程", "答疑/补充")],

    ["gcjs_zhongbiao_shuili_gg",
     "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=0"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "水利工程", "结果公示"), gcjs(f2, "水利工程", "结果公示")],

    # 土地开发整理
    ["gcjs_zhaobiao_tudi_gg",
     "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=0"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "土地开发整理", "招标公告"), gcjs(f2, "土地开发整理", "招标公告")],

    ["gcjs_zhongbiaohx_tudi_gg",
     "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=0"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "土地开发整理", "中标候选人公示"), gcjs(f2, "土地开发整理", "中标候选人公示")],

    ["gcjs_gqita_bian_da_tudi_gg",
     "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=0"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "土地开发整理", "答疑/补充"), gcjs(f2, "土地开发整理", "答疑/补充")],

    ["gcjs_zhongbiao_tudi_gg",
     "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=0"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "土地开发整理", "结果公示"), gcjs(f2, "土地开发整理", "结果公示")],

    # 其他项目
    ["gcjs_zhaobiao_qita_gg",
     "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=0"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "其他项目", "招标公告"), gcjs(f2, "其他项目", "招标公告")],

    ["gcjs_zhongbiaohx_qita_gg",
     "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=0"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "其他项目", "中标候选人公示"), gcjs(f2, "其他项目", "中标候选人公示")],

    ["gcjs_gqita_bian_da_qita_gg",
     "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=0"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "其他项目", "答疑/补充"), gcjs(f2, "其他项目", "答疑/补充")],

    ["gcjs_zhongbiao_qita_gg",
     "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=0"
        , ["name", "href", "ggstart_time", "info"], gcjs(f1, "其他项目", "结果公示"), gcjs(f2, "其他项目", "结果公示")],

    ##政府采购
    ["zfcg_zhongbiao_gg",
     "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=1"
        , ["name", "href", "ggstart_time", "info"], zfcg(f1, "公开招标", "中标结果"), zfcg(f2, "公开招标", "中标结果")],

    ["zfcg_gqita_bian_da_gg",
     "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=1"
        , ["name", "href", "ggstart_time", "info"], zfcg(f1, "公开招标", "答疑变更"), zfcg(f2, "公开招标", "答疑变更")],

    ["zfcg_zhaobiao_gg",
     "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=1"
        , ["name", "href", "ggstart_time", "info"], zfcg(f1, "公开招标", "采购公告"), zfcg(f2, "公开招标", "采购公告")]
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖南省张家界市", **args)
    est_html(conp, f=f3, **args)


#
if __name__ == '__main__':
    # work(conp=["postgres", "since2015", "192.168.4.175", "hunan", "zhangjiajie"])
#
    driver=webdriver.Chrome()
    # url = "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=1"
    # driver.get(url)
    # df = gcjs(f2,"公开招标","中标结果")(driver)
    # print(df)
    # driver=webdriver.Chrome()
    # url = "http://www.zjjsggzy.gov.cn/Home/JYList?index%20=%200&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xdex=1"
    # driver.get(url)
    # for i in range(1,5):
    #     df=gcjs(f1,"公开招标","中标结果")(driver, i)
    #     print(df.values)
    #     for i in df[1].values:
    #         print(i)
#             print(f)
    f = f3(driver, 'http://www.zjjsggzy.gov.cn/新流程/招投标信息/jyxx_1.html?iq=gc&type=招标公告&tpid=59df2c21adc29af4dc63727e&tpTitle=%E6%AD%A6%E9%99%B5%E6%BA%90%E5%8C%BA%E4%B8%AD%E6%B9%96%E4%B9%A1%E9%B1%BC%E6%B3%89%E5%B3%AA%E6%9D%91%E5%B0%8F%E5%AD%A6%E6%95%99%E5%AD%A6%E6%A5%BC%E5%8F%8A%E9%99%84%E5%B1%9E%E5%B7%A5%E7%A8%8B')
    print(f)