import json
import re
import requests
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong.util.etl import est_html, est_meta, add_info
import time
import math
_name_ = "suqian"


def f2(driver):
    # WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH,'//div[@class="ewb-bread"]/a[last()]')))
    if '其他交易' in WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH,'//div[@class="ewb-bread"]/a[last()]'))).text:
        params = "001007"
    else:
        locator = (By.XPATH, "//li/a[contains(@style,'font')]")
        js_temp = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute("onclick")
        params = re.findall("\'([^\']+)", js_temp)[0]
    data2 = {
        'categorynum': params,
        'city': '',
        'xmmc': '',
    }
    url2 = "http://ggzy.sqzwfw.gov.cn/WebBuilder/jyxxAction.action?cmd=getListByCount"
    content2 = json.loads(requests.post(url2, data=data2).text)
    page_total = math.ceil(content2['custom']/10)

    driver.quit()
    return int(page_total)


def f1(driver, num):
    if '其他交易' in WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH,'//div[@class="ewb-bread"]/a[last()]'))).text:
        params = "001007"
    else:
        locator = (By.XPATH, "//li/a[contains(@style,'font')]")
        js_temp = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute("onclick")
        params = re.findall("\'([^\']+)", js_temp)[0]

    pa_data = {
        'categorynum': params,
        'city': '',
        'xmmc': '',
        'pageIndex': num,
        'pageSize': '10',
    }
    url = "http://ggzy.sqzwfw.gov.cn/WebBuilder/jyxxAction.action?cmd=getList"
    page = json.loads(requests.post(url, data=pa_data).text)
    data = []
    content_list = json.loads(page['custom'])['Table']

    for content in content_list:
        name = content["title"]
        project_type = content['type']
        area = content['city']
        ggstart_time = content['postdate']
        href = "http://ggzy.sqzwfw.gov.cn" + content['href']
        info =json.dumps({"project_type":project_type,'area':area})
        temp = [name, ggstart_time, href,info]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    return df


def before(f, xmtype, ggtype):
    def wrap(*args):
        driver = args[0]
        switch(driver, xmtype, ggtype)
        return f(*args)
    return wrap


type = {
    "建设工程": ["search2('001001','','')",
             {"招标预公告": "search2('001001010','','')",
              "招标公告/资审公告": "search2('001001001','','')",
              "未入围公示": "search2('001001003','','')",
              "最高限价公示": "search2('001001004','','')",
              "评标结果公示": "search2('001001005','','')",
              "中标结果公告": "search2('001001006','','')",
              "直接发包结果公告": "search2('001001011','','')",
              "答疑澄清": "search2('001001002','','')",
              "中标单位变更": "search2('001001012','','')"}],
    "交通工程": ["search2('001002','','')",
             {"招标预公告": "search2('001002007','','')",
              "招标公告/资审公告": "search2('001002001','','')",
              "最高限价公示": "search2('001002009','','')",
              "评标结果公示": "search2('001002003','','')",
              "中标结果公告": "search2('001002004','','')",
              "直接发包结果公告": "search2('001002010','','')"}],
    "水利工程": ["search2('001003','','')",
             {"招标预公告": "search2('001003008','','')",
              "招标公告/资审公告": "search2('001003001','','')",
              "最高限价公示": "search2('001003010','','')",
              "中标结果公告": "search2('001003004','','')",
              "评标结果公示": "search2('001003003','','')",
              "直接发包结果公告": "search2('001003011','','')",
              "中标单位变更": "search2('001003013','','')"}],
    "政府采购": ["search2('001004','','')",
             {"采购预告": "search2('001004001','','')",
              "采购公告": "search2('001004002','','')",
              "更正公告": "search2('001004003','','')",
              "结果公告": "search2('001004006','','')",
              "中标单位变更": "search2('001004009','','')",
              "单一来源公示": "search2('001004008','','')",
              }],
    "其他交易": "search2('001007','','')"}


def switch(driver, xmtype, ggtype):
    if xmtype == "其他交易":driver.execute_script(type[xmtype])
    else:driver.execute_script(type[xmtype][1][ggtype])
    time.sleep(1)


def f3(driver, url):
    driver.get(url)
    try:
        locator = (By.XPATH, "//div[@class='article-info']")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        flag = True
    except:
        locator = (By.CLASS_NAME, "ewb-container clearfix")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
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
        div = soup.find('div', class_='article-info')
    else:
        div = soup.find('div', class_='ewb-container clearfix')
    return div


def work(conp, **kwargs):
    est_meta(conp, data=data, diqu="江苏省宿迁市", **kwargs)
    est_html(conp, f=f3, **kwargs)


data = [
    # 工程建设
    ["gcjs_yucai_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "建设工程", "招标预公告"), before(f2, "建设工程", "招标预公告")],
    ["gcjs_zhaobiao_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "建设工程", "招标公告/资审公告"), before(f2, "建设工程", "招标公告/资审公告")],
    ["gcjs_zgysjg_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "建设工程", "未入围公示"), before(f2, "建设工程", "未入围公示")],
    ["gcjs_kongzhijia_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "建设工程", "最高限价公示"), before(f2, "建设工程", "最高限价公示")],
    ["gcjs_zhongbiaohx_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "建设工程", "评标结果公示"), before(f2, "建设工程", "评标结果公示")],
    ["gcjs_zhongbiao_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "建设工程", "中标结果公告"), before(f2, "建设工程", "中标结果公告")],
    ["gcjs_zhaobiao_zjfb_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     add_info(before(f1, "建设工程", "直接发包结果公告"),{"method":"直接发包"}), before(f2, "建设工程", "直接发包结果公告")],
    ["gcjs_biangeng_zhongbiao_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "建设工程", "中标单位变更"), before(f2, "建设工程", "中标单位变更")],
    ["gcjs_dayi_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "建设工程", "答疑澄清"), before(f2, "建设工程", "答疑澄清")],
    # 交通
    ["gcjs_jiaotong_yucai_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "交通工程", "招标预公告"), before(f2, "交通工程", "招标预公告")],
    ["gcjs_jiaotong_zhaobiao_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "交通工程", "招标公告/资审公告"), before(f2, "交通工程", "招标公告/资审公告")],
    ["gcjs_jiaotong_kongzhijia_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "交通工程", "最高限价公示"), before(f2, "交通工程", "最高限价公示")],
    ["gcjs_jiaotong_zhongbiaohx_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "交通工程", "评标结果公示"), before(f2, "交通工程", "评标结果公示")],
    ["gcjs_jiaotong_zhongbiao_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "交通工程", "中标结果公告"), before(f2, "交通工程", "中标结果公告")],
    ["gcjs_jiaotong_zhaobiao_zjfb_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     add_info(before(f1, "交通工程", "直接发包结果公告"),{"method":"直接发包"}), before(f2, "交通工程", "直接发包结果公告")],
    # # 水利
    ["gcjs_shuili_yucai_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "水利工程", "招标预公告"), before(f2, "水利工程", "招标预公告")],
    ["gcjs_shuili_zhaobiao_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "水利工程", "招标公告/资审公告"), before(f2, "水利工程", "招标公告/资审公告")],
    ["gcjs_shuili_kongzhijia_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "水利工程", "最高限价公示"), before(f2, "水利工程", "最高限价公示")],
    ["gcjs_shuili_zhongbiaohx_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "水利工程", "评标结果公示"), before(f2, "水利工程", "评标结果公示")],
    ["gcjs_shuili_zhongbiao_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "水利工程", "中标结果公告"), before(f2, "水利工程", "中标结果公告")],
    ["gcjs_shuili_zhaobiao_zjfb_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     add_info(before(f1, "水利工程", "直接发包结果公告"),{"method":"直接发包"}), before(f2, "水利工程", "直接发包结果公告")],
    ["gcjs_shuili_biangeng_zhongbiaodw_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     add_info(before(f1, "水利工程", "中标单位变更"),{'tag':'中标单位变更'}), before(f2, "水利工程", "中标单位变更")],

    ["zfcg_yucai_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "政府采购", "采购预告"), before(f2, "政府采购", "采购预告")],
    ["zfcg_zhaobiao_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "政府采购", "采购公告"), before(f2, "政府采购", "采购公告")],
    ["zfcg_biangeng_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "政府采购", "更正公告"), before(f2, "政府采购", "更正公告")],
    ["zfcg_zhongbiao_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "政府采购", "结果公告"), before(f2, "政府采购", "结果公告")],
    ["zfcg_biangeng_zhongbiaodw_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     add_info(before(f1, "政府采购", "中标单位变更"),{'tag':'中标单位变更'}), before(f2, "政府采购", "中标单位变更")],
    ["zfcg_zhaobiao_dyly_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     add_info(before(f1, "政府采购", "单一来源公示"),{"method":"单一来源"}), before(f2, "政府采购", "单一来源公示")],
    #
    ["jqita_gqita_zhao_liu_zhong_gg", "http://ggzy.sqzwfw.gov.cn/jyxx/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     before(f1, "其他交易", "无"), before(f2, "其他交易", "无")],
]

if __name__ == '__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "jiangsu", "suqian"]
    work(conp)
