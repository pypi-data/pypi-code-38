import json
import math
import re
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong.util.etl import est_html, est_meta, add_info
import requests
from time import sleep

_name_ = "nantong"


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='article-info']")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    before = len(driver.page_source)
    sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 5: break

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_='article-info')
    return div


def f1(driver, num):
    categorynum = driver.current_url.split('=')[1]
    url = "http://ggzyjy.nantong.gov.cn/services/XzsJsggWebservice/getList"
    param = {'response': 'application/json', 'categorynum': categorynum, 'xmbh': '', 'xmmc': '', "diqu2": '',
             "pageIndex": num, "pageSize": 15}
    driver_info = webdriver.DesiredCapabilities.CHROME

    if "--proxy" in driver_info['goog:chromeOptions']['args'][0]:
        proxy_ip = driver_info['goog:chromeOptions']['args'][0].split('=')[1].split('://')
        proxies = {proxy_ip[0]: proxy_ip[1]}
    else:
        proxies = {}

    page = json.loads(requests.get(url, proxies=proxies, params=param, timeout=60).text)['return']

    content_list = json.loads(page).get('Table')
    data = []
    for content in content_list:
        info = {}

        ggstart_time = content.get('postdate')
        name = re.sub(r'<[^>]*?>', '', content.get("title"))
        href = 'http://ggzyjy.nantong.gov.cn' + content.get("href")
        ggtype = content.get("jyfl")
        area = content.get("city")
        method = content.get("jyfs")
        if method != None: info["method"] = method
        if ggtype != None: info["ggtype"] = ggtype
        if area != None: info["area"] = area
        # info = json.dumps({"ggtype": ggtype, "area": area,"method":method}, ensure_ascii=False)
        info = json.dumps(info, ensure_ascii=False)
        temp = [name, ggstart_time, href, info]
        data.append(temp)

    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    categorynum = driver.current_url.split('=')[1]
    url = "http://ggzyjy.nantong.gov.cn/services/XzsJsggWebservice/getListByCount"
    param = {'response': 'application/json', 'categorynum': categorynum, 'xmbh': '', 'xmmc': '', "diqu2": ''}
    driver_info = webdriver.DesiredCapabilities.CHROME
    try:
        if "--proxy" in driver_info['goog:chromeOptions']['args'][0]:

            proxy_ip = driver_info['goog:chromeOptions']['args'][0].split('=')[1]
        else:
            proxy_ip = {}
    except:
        proxy_ip = {}
    total_page = math.ceil(json.loads(requests.get(url, proxies=proxy_ip, params=param).text)['return'] / 15)
    driver.quit()
    return total_page


data = [

    # 工程建设
    ["gcjs_zhaobiao_gg", "http://ggzyjy.nantong.gov.cn/jsgc/proInfo.html?type=003001001",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    #
    ["gcjs_zgysjg_gg", "http://ggzyjy.nantong.gov.cn/jsgc/proInfo.html?type=003001006",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    #
    ["gcjs_kongzhijia_gg", "http://ggzyjy.nantong.gov.cn/jsgc/proInfo.html?type=003001005",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    #
    ["gcjs_zhongbiao_gg", "http://ggzyjy.nantong.gov.cn/jsgc/proInfo.html?type=003001008",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    #                       http://ggzyjy.nantong.gov.cn/jsgc/proInfo.html?type=jsgc
    ["gcjs_zhongbiaohx_gg", "http://ggzyjy.nantong.gov.cn/jsgc/proInfo.html?type=003001007",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    #                       http://ggzyjy.nantong.gov.cn/jsgc/proInfo.html?type=jsgc
    ["gcjs_zhongbiaohx_2_gg", "http://ggzyjy.nantong.gov.cn/jsgc/proInfo.html?type=003001010",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["gcjs_liubiao_gg", "http://ggzyjy.nantong.gov.cn/jsgc/proInfo.html?type=003001009",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],

    # 交通
    ["gcjs_jiaotong_zhaobiao_gg", "http://ggzyjy.nantong.gov.cn/jtgc/proInfo.html?type=003002001",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["gcjs_jiaotong_zhongbiaohx_gg", "http://ggzyjy.nantong.gov.cn/jtgc/proInfo.html?type=003002003",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["gcjs_jiaotong_zhongbiao_gg", "http://ggzyjy.nantong.gov.cn/jtgc/proInfo.html?type=003002004",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    # 港口
    ["gcjs_gangkou_zhaobiao_gg", "http://ggzyjy.nantong.gov.cn/jtgc/proInfo.html?type=003010001",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["gcjs_gangkou_biangeng_gg", "http://ggzyjy.nantong.gov.cn/jtgc/proInfo.html?type=003010002",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["gcjs_gangkou_zhongbiao_gg", "http://ggzyjy.nantong.gov.cn/jtgc/proInfo.html?type=003010003",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    # 水利
    ["gcjs_shuili_zhaobiao_gg", "http://ggzyjy.nantong.gov.cn/slgc/proInfo.html?type=003003001",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["gcjs_shuili_zhongbiaohx_gg", "http://ggzyjy.nantong.gov.cn/slgc/proInfo.html?type=003003003",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["gcjs_shuili_zhongbiao_gg", "http://ggzyjy.nantong.gov.cn/slgc/proInfo.html?type=003003004",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["gcjs_shuili_dayi_gg", "http://ggzyjy.nantong.gov.cn/slgc/proInfo.html?type=003003002",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],

    # 政府采购
    ["zfcg_gqita_bian_bu_gg", "http://ggzyjy.nantong.gov.cn/zfcg/proInfo.html?type=003004010003",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_gg", "http://ggzyjy.nantong.gov.cn/zfcg/proInfo.html?type=003004010002",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_yucai_gg", "http://ggzyjy.nantong.gov.cn/zfcg/proInfo.html?type=003004010001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://ggzyjy.nantong.gov.cn/zfcg/proInfo.html?type=003004010005",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_gg", "http://ggzyjy.nantong.gov.cn/zfcg/proInfo.html?type=003004010004",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_hetong_gg", "http://ggzyjy.nantong.gov.cn/zfcg/proInfo.html?type=003004010006",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gkzb_gg", "http://ggzyjy.nantong.gov.cn/zfcg/proInfo.html?type=003004010007",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"method": "公开招标"}), f2],
    ["zfcg_zhaobiao_yqzb_gg", "http://ggzyjy.nantong.gov.cn/zfcg/proInfo.html?type=003004010008",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"method": "邀请招标"}), f2],
    ["zfcg_zhaobiao_jzxtp_gg", "http://ggzyjy.nantong.gov.cn/zfcg/proInfo.html?type=003004010009",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"method": "竞争性谈判"}), f2],
    ["zfcg_zhaobiao_jzxcs_gg", "http://ggzyjy.nantong.gov.cn/zfcg/proInfo.html?type=003004010010",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"method": "竞争性磋商"}), f2],
    ["zfcg_zhaobiao_dyly_gg", "http://ggzyjy.nantong.gov.cn/zfcg/proInfo.html?type=003004010011",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"method": "单一来源"}), f2],
    ["zfcg_zhaobiao_xj_gg", "http://ggzyjy.nantong.gov.cn/zfcg/proInfo.html?type=003004010012",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"method": "询价"}), f2],
    ["zfcg_zhaobiao_xygh_gg", "http://ggzyjy.nantong.gov.cn/zfcg/proInfo.html?type=003004010013",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"method": "协议供货"}), f2],
    ["zfcg_zhaobiao_wsjj_gg", "http://ggzyjy.nantong.gov.cn/zfcg/proInfo.html?type=003004010014",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"method": "网上竞价"}), f2],

    ["zfcg_zhaobiao_fensan_gg", "http://ggzyjy.nantong.gov.cn/zfcg/proInfo.html?type=003004011001",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "分散"}), f2],
    ["zfcg_biangeng_fensan_gg", "http://ggzyjy.nantong.gov.cn/zfcg/proInfo.html?type=003004011002",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "分散"}), f2],
    ["zfcg_zhongbiao_fensan_gg", "http://ggzyjy.nantong.gov.cn/zfcg/proInfo.html?type=003004011003",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "分散"}), f2],

    ["yiliao_biangeng_gg", "http://ggzyjy.nantong.gov.cn/ylsb/proInfo.html?type=003007002",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["yiliao_zhaobiao_gg", "http://ggzyjy.nantong.gov.cn/ylsb/proInfo.html?type=003007001",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["yiliao_zhongbiao_gg", "http://ggzyjy.nantong.gov.cn/ylsb/proInfo.html?type=003007003",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    #
    ["jqita_zhaobiao_gg", "http://ggzyjy.nantong.gov.cn/qt/proInfo.html?type=003009004001",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["jqita_biangeng_gg", "http://ggzyjy.nantong.gov.cn/qt/proInfo.html?type=003009004002",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["jqita_zhongbiao_gg", "http://ggzyjy.nantong.gov.cn/qt/proInfo.html?type=003009004003",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    # 机电设备
    ["zfcg_zhaobiao_jdsb_gg", "http://ggzyjy.nantong.gov.cn/qt/proInfo.html?type=003008001",
     ["name", "ggstart_time", "href", "info"],
     add_info(f1, {"tag": "机电设备"}), f2],
    ["zfcg_biangeng_jdsb_gg", "http://ggzyjy.nantong.gov.cn/qt/proInfo.html?type=003008002",
     ["name", "ggstart_time", "href", "info"],
     add_info(f1, {"tag": "机电设备"}), f2],
    ["zfcg_zhongbiao_jdsb_gg", "http://ggzyjy.nantong.gov.cn/qt/proInfo.html?type=003008003",
     ["name", "ggstart_time", "href", "info"],
     add_info(f1, {"tag": "机电设备"}), f2],

]


def work(conp, **kwargs):
    est_meta(conp, data=data, diqu="江苏省南通市", **kwargs)
    est_html(conp, f=f3, **kwargs)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "jiangsu", "nantong"]
    work(conp, num=4, total=10)
    # f2(d)
    # d = webdriver.Chrome()
    # d.get(url)
    # f1(d,1)
    # f1(d,5)
