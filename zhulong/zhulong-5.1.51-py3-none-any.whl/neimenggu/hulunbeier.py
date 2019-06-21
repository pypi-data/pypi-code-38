import json
import math
import re
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
import pandas as pd
from zhulong.util.etl import est_meta, est_html
from urllib import parse
_name_ = "hulunbeier"


def f1(driver, num):
    param_list = parse.parse_qs(driver.current_url.split('?')[1])
    xxlx = param_list.get('xx')
    zhu = param_list.get('zhu')

    siteInfo = driver.execute_script("return siteInfo")
    params = {
        'cmd': 'getInfolist',
        'siteGuid': siteInfo['siteGuid'],
        'pageIndex': num,
        'pageSize': 16,
        'xxlx': xxlx,
        'fbsj': '',
        'dqfb': '',
        'jylx': '',
        'categoryzhu': zhu,
        '_': int(time.time()*1000)
    }
    data =[]
    page = requests.get("http://www.hlbeggzyjy.org.cn/Epoint_hlbeggzy/jyxxlistaction.action", params=params).text
    json.loads(page)
    content_list = json.loads(json.loads(page).get('custom')).get('Table')
    for content in content_list:
        name = content.get("title")
        ggstart_time = content.get("date")
        url = "http://www.hlbeggzyjy.org.cn" + content.get("href")
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)

    df["info"] = None
    driver.refresh()
    return df


def f2(driver):
    param_list = parse.parse_qs(driver.current_url.split('?')[1])
    xxlx = param_list.get('xx')
    zhu = param_list.get('zhu')
    siteInfo = driver.execute_script("return siteInfo")
    params = {
        'cmd': 'getInfolistBycount',
        'siteGuid': siteInfo['siteGuid'],
        'xxlx': xxlx,
        'fbsj': '',
        'dqfb': '',
        'jylx': '',
        'categoryzhu': zhu,
        '_': int(time.time()*1000)
    }

    total_temp = json.loads(requests.get("http://www.hlbeggzyjy.org.cn/Epoint_hlbeggzy/jyxxlistaction.action",params=params).text).get('custom')
    total_page = math.ceil(total_temp/16)
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    try:
        locator = (By.XPATH, "//div[@class='ewb-main']")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag = True
    except:
        locator = (By.XPATH, "//div[@class='news-article']")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag = False
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
    if flag:
        div = soup.find('div', class_='ewb-main')
    else:
        div = soup.find('div', class_='news-article')
    return div


def switch(driver, ggtype, xmtype):
    locator = (By.XPATH, "//div[@class='tab-panel']//ul[@class='wb-data-item']/li[2]/div/a")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    val = driver.find_element_by_xpath("//div[@class='tab-panel']//ul[@class='wb-data-item']/li[1]/div/a").get_attribute("href")
    if ggtype == "政府采购":
        flag = 2
    else:
        flag = 1
    driver.find_element_by_xpath('//div[@class="ewb-query-hd"]/ul/li[%s]'%flag).click()
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH,'//div[@class="ewb-query-hd"]/ul/li[%s][contains(@class,"current")]'%(flag))))
    driver.execute_script(gg_type[ggtype][xmtype])
    locator = (By.XPATH, "//div[@class='tab-panel']//ul[@class='wb-data-item']/li[2]/div/a")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='tab-panel']//ul[@class='wb-data-item']/li[1]/div/a[not(contains(@href,'%s'))]" % val)
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))


def before(f, ggtype, xmtype):
    def wrap(*args):
        driver = args[0]
        switch(driver, ggtype, xmtype)
        return f(*args)

    return wrap


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.hlbeggzyjy.org.cn/gcjs/subpage-jyxx.html?xx=008001001001&zhu=021",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_biangeng_gg",
     "http://www.hlbeggzyjy.org.cn/gcjs/subpage-jyxx.html?xx=008001001002&zhu=021",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://www.hlbeggzyjy.org.cn/gcjs/subpage-jyxx.html?xx=008001001005&zhu=021",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://www.hlbeggzyjy.org.cn/gcjs/subpage-jyxx.html?xx=008001001006&zhu=021",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_liubiao_gg",
     "http://www.hlbeggzyjy.org.cn/gcjs/subpage-jyxx.html?xx=008001001007&zhu=021",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_bian_cheng_gg",
     "http://www.hlbeggzyjy.org.cn/gcjs/subpage-jyxx.html?xx=008001001004&zhu=021",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://www.hlbeggzyjy.org.cn/gcjs/subpage-jyxx.html?xx=008001002001&zhu=022",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://www.hlbeggzyjy.org.cn/gcjs/subpage-jyxx.html?xx=008001002002&zhu=022",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://www.hlbeggzyjy.org.cn/gcjs/subpage-jyxx.html?xx=008001002005&zhu=022",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_gg",
     "http://www.hlbeggzyjy.org.cn/gcjs/subpage-jyxx.html?xx=008001002006&zhu=022",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_gqita_bian_cheng_gg",
     "http://www.hlbeggzyjy.org.cn/gcjs/subpage-jyxx.html?xx=008001002004&zhu=022",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

gg_type = {
    "工程建设": {
        "招标公告": "searchjy('021','008001001001','','','',this)",
        "变更公告": "searchjy('021','008001001002','','','',this)",
        "中标候选人公示": "searchjy('021','008001001005','','','',this)",
        "中标结果公告": "searchjy('021','008001001006','','','',this)",
        "招标异常公告": "searchjy('021','008001001007','','','',this)",
        "澄清补疑":"searchjy('021','008001001004','','','',this)"
    },
    "政府采购": {
        "采购公告": "searchjy2('022','008001002001','','','',this)",
        "变更公告": "searchjy2('022','008001002002','','','',this)",
        "中标公示": "searchjy2('022','008001002005','','','',this)",
        "废标公告": "searchjy2('022','008001002006','','','',this)",
        "澄清补疑":"searchjy2('022','008001002004','','','',this)"
    },
}


def work(conp, **kwargs):
    est_meta(conp, data=data, diqu="内蒙古自治区呼伦贝尔市", **kwargs)
    est_html(conp, f=f3, **kwargs)


if __name__ == "__main__":

    work(conp=["postgres", "since2015", "192.168.3.171", "neimenggu", "hulunbeier"],num=4)
    # driver = webdriver.Chrome()
    # driver.get("http://www.hlbeggzyjy.org.cn/gcjs/subpage-jyxx.html?xx=008001001001&zhu=021?xx=008001002001&zhu=022")
    # print(f2(driver))
    # f1(driver,3)