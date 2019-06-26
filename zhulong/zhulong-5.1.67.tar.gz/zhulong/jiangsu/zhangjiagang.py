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
from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, add_info
import requests
import time

_name_ = "zhangjiagang"


def f3(driver, url):
    driver.get(url)
    try:
        locator = (By.XPATH, "//table[@id='tblInfo']")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        flag = True
    except:
        locator = (By.ID, "InfoDetail1_tblInfo")
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
        div = soup.find('table', id='tblInfo')
    else:
        div = soup.find('table', id='InfoDetail1_tblInfo')

    return div


def f1(driver, num):
    locator = (By.XPATH, "//*[@id='right']/table/tbody/tr")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//tr[@height='25'][1]/td/a").get_attribute("href")[-40:]
    locator = (By.CLASS_NAME, 'huifont')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    cnum = driver.find_element_by_class_name('huifont').text.split('/')[0]
    if int(cnum) != int(num):
        url = re.sub('Paging=\d+', 'Paging=' + str(num), driver.current_url)
        driver.get(url)
        for _ in range(3):
            try:
                locator = (By.XPATH, "//tr[@height='25'][1][not(contains(@href,'%s'))]" % val)
                WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
                break
            except:
                driver.refresh()

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//tr[@height='25']")
    for content in content_list:
        if content.xpath("./td/a/text()") == []:
            name = "None"
        else:
            name = content.xpath("./td/a/text()")[0].strip()
        try:
            ggstart_time = content.xpath("./td[2]/text()")[0].strip()
        except:
            ggstart_time = content.xpath("./td[3]/text()")[0].strip()
        url = "http://ggzy.zjg.gov.cn" + content.xpath("./td/a/@href")[0]
        temp = [name, ggstart_time, url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.CLASS_NAME, 'huifont')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    total_page = int(driver.find_element_by_class_name('huifont').text.split('/')[1])
    driver.quit()
    return total_page


data = [

    ["gcjs_zhaobiao_gg", "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010001/010001008/010001008001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010001/010001008/010001008003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg", "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010001/010001008/010001008002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_jiaotong_zhaobiao_gg", "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010001/010001010/010001010001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_jiaotong_zhong_zhonghx_gg",
     "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010001/010001010/010001010002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_shuili_zhaobiao_gg", "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010001/010001009/010001009001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuili_zhongbiaohx_gg", "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010001/010001009/010001009003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuili_zhongbiao_gg", "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010001/010001009/010001009002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_qita_zhaobiao_gg", "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010001/010001011/010001011001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'其他工程'}), f2],
    ["gcjs_qita_zhongbiao_gg", "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010001/010001011/010001011002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'其他工程'}), f2],

    ["zfcg_zhaobiao_hw_bgsb_gg",
     "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002001/010002001001/010002001001001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type1": "货物","type2": "电脑及办公设备"}), f2],
    ["zfcg_zhaobiao_hw_jiajv_gg",
     "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002001/010002001001/010002001001002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type1": "货物","type2": "家具"}), f2],
    ["zfcg_zhaobiao_hw_ylsb_gg",
     "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002001/010002001001/010002001001003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type1": "货物","type2": "医疗"}), f2],
    ["zfcg_zhaobiao_hw_jd_gg",
     "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002001/010002001001/010002001001004?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type1": "货物","type2": "机电"}), f2],
    ["zfcg_zhaobiao_hw_jtgj_gg",
     "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002001/010002001001/010002001001005?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type1": "货物","type2": "交通工具及特种车辆"}), f2],
    ["zfcg_zhaobiao_hw_zysb_gg",
     "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002001/010002001001/010002001001006/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type1": "货物","type2": "专用设备"}), f2],
    ["zfcg_zhaobiao_hw_qita_gg",
     "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002001/010002001001/010002001001007/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gc_gg", "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002001/010002001002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_fw_srsz_gg",
     "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002001/010002001003/010002001003001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type1": "服务","type2": "市容市政"}), f2],
    ["zfcg_zhaobiao_fw_yxbz_gg",
     "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002001/010002001003/010002001003002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type1": "服务","type2": "运行保障"}), f2],
    ["zfcg_zhaobiao_fw_glzx_gg",
     "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002001/010002001003/010002001003004/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type1": "服务","type2": "管理咨询"}), f2],
    ["zfcg_zhaobiao_fw_qita_gg",
     "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002001/010002001003/010002001003007/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_hw_gg", "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002002/010002002001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type1": "货物"}), f2],
    ["zfcg_biangeng_fw_gg", "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002002/010002002003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type1": "服务"}), f2],
    ###
    ["zfcg_zhongbiao_hw_bbgsb_gg",
     "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002003/010002003001/010002003001001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type1": "货物","type2": "办公自动化设备"}), f2],
    ["zfcg_zhongbiao_hw_jj_gg",
     "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002003/010002003001/010002003001002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type1": "货物","type2": "家具"}), f2],

    ["zfcg_zhongbiao_hw_ylsb_gg",
     "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002003/010002003001/010002003001005/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type1": "货物","type2": "医疗设备"}), f2],

    ["zfcg_zhongbiao_hw_jtgj_gg",
     "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002003/010002003001/010002003001003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type1": "货物","type2": "交通工具及特种车辆"}), f2],

    ["zfcg_zhongbiao_hw_zysb_gg",
     "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002003/010002003001/010002003001004/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type1": "货物","type2": "专业设备"}), f2],
    ["zfcg_zhongbiao_hw_qita_gg",
     "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002003/010002003001/010002003001006/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gc_gg", "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002003/010002003002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_fw_srsz_gg",
     "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002003/010002003003/010002003003001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type1": "服务","type2": "市容市政"}), f2],
    ["zfcg_zhongbiao_fw_xxjsfw_gg",
     "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002003/010002003003/010002003003002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type1": "服务","type2": "信息技术服务"}), f2],
    ["zfcg_zhongbiao_fw_wxby_gg",
     "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002003/010002003003/010002003003005/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type1": "服务","type2": "维修保养"}), f2],
    ["zfcg_zhongbiao_fw_qita_gg",
     "http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010002/010002003/010002003003/010002003003008/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **kwargs):
    est_meta(conp, data=data, diqu="江苏省张家港市", **kwargs)
    est_html(conp, f=f3, **kwargs)


if __name__ == "__main__":

    # conp=["postgres", "since2015", "192.168.3.171", "jiangsu", "zhangjiagang"]
    driver = webdriver.Chrome()
    driver.get("http://ggzy.zjg.gov.cn/ggzyweb/jyxx/010001/010001008/010001008001/?Paging=1")
    for i in range(1, 250): f1(driver, i)
