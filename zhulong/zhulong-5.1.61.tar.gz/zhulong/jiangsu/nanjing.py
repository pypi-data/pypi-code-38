import json
import random
import re
import time

from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong.util.etl import est_meta, est_html, add_info

_name_ = "nanjing"


def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='ewb-info-items']")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))

    locator = (By.XPATH, '//div[@class="ewb-page"]')
    cnum_temp = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text
    cnum = 1 if cnum_temp == '' else int(
        driver.find_element_by_xpath('//span[contains(@id,"index")]').text.split('/')[0])
    val = driver.find_element_by_xpath('//ul[@class="ewb-info-items"]/li[1]').get_attribute("onclick")[-60:]
    if int(num) != int(cnum):
        url = re.sub("[\d\w]+\.html", str(num) + '.html', driver.current_url)
        driver.get(url)
        locator = (By.XPATH, '//ul[@class="ewb-info-items"]/li[1][not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@class="ewb-info-items"]/li')
    for content in content_list:
        url = 'http://ggzy.njzwfw.gov.cn' + re.findall(r"\'([^\']+)", content.xpath("./@onclick")[0])[0]
        length_col = len(content.xpath('./div'))
        if length_col == 2:

            try:name = content.xpath('./div[1]/p/text()')[0]
            except:name = None
            ggstart_time = content.xpath('./div[last()]/p/text()')[0]
            info = None
        elif length_col == 4:
            try:project_code = content.xpath('./div[1]/p/text()')[0]
            except:project_code = None
            try:name = content.xpath('./div[2]/p/text()')[0]
            except:name = None

            try:belong = content.xpath('./div[3]/p/text()')[0]
            except:belong = None
            info = json.dumps({"project_code": project_code, "belong": belong}, ensure_ascii=False)
            ggstart_time = content.xpath('./div[last()]/p/text()')[0]
        elif length_col == 6:
            try:project_code = content.xpath('./div[1]/p/text()')[0]
            except:project_code = None

            try:name = content.xpath('./div[2]/p/text()')[0]
            except:name = None

            try:project_type = content.xpath('./div[3]/p/text()')[0]
            except:project_type = None

            try:money = content.xpath('./div[4]/p/text()')[0]
            except:money = None

            ggstart_time = content.xpath('./div[5]/p/text()')[0]
            ggstart_end = content.xpath('./div[last()]/p/text()')[0]
            info = json.dumps(
                {'project_code': project_code, "project_type": project_type, "money": money, "ggend_time": ggstart_end},
                ensure_ascii=False)
        else:
            try:project_code = content.xpath('./div[1]/p/text()')[0]
            except:project_code = None

            try:name = content.xpath('./div[2]/p/text()')[0]
            except:name = None

            try:project_type = content.xpath('./div[3]/p/text()')[0]
            except:project_type = None

            try:money = content.xpath('./div[4]/p/text()')[0]
            except:money = None

            try:ggstart_time = content.xpath('./div[last()]/p/text()')[0]
            except:ggstart_time = None
            info = json.dumps({'project_code': project_code, "project_type": project_type, "money": money},ensure_ascii=False)

        if '-' not in ggstart_time:ggstart_time='none'
        temp = [name, ggstart_time, url, info]
        data.append(temp)


    df = pd.DataFrame(data=data)
    df=df.loc[df[df.columns[1]].notnull() &df[df.columns[0]].notnull()&df[df.columns[2]].notnull() ]
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="ewb-page"]')
    page_temp = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text
    total_page = 1 if page_temp == '' else int(
        driver.find_element_by_xpath('//span[contains(@id,"index")]').text.split('/')[1])
    driver.quit()
    return total_page


def f3(driver, url):
    driver.get(url)
    locator = (By.CLASS_NAME, "article-info")
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
    div = soup.find('div', class_='article-info')
    return div


data = [
    # # # 房建市政
    ["gcjs_fangjianshizheng_zhaobiao_fw_gg", "http://ggzy.njzwfw.gov.cn/njweb/fjsz/068001/068001001/moreinfo.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "房建市政","type":"服务"}), f2],
    ["gcjs_fangjianshizheng_zhaobiao_gc_gg", "http://ggzy.njzwfw.gov.cn/njweb/fjsz/068001/068001002/moreinfo.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "房建市政","type":"工程"}), f2],
    ["gcjs_fangjianshizheng_zhaobiao_xxgc_gg", "http://ggzy.njzwfw.gov.cn/njweb/fjsz/068001/068001003/moreinfo4a.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "房建市政","type":"小型工程"}), f2],

    ["gcjs_fangjianshizheng_zhongbiaohx_gc_gg", "http://ggzy.njzwfw.gov.cn/njweb/fjsz/068002/068002001/moreinfo2.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "房建市政","type":"工程"}), f2],
    ["gcjs_fangjianshizheng_zhongbiaohx_fw_gg", "http://ggzy.njzwfw.gov.cn/njweb/fjsz/068002/068002002/moreinfo2.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "房建市政","type":"服务"}), f2],
    #
    ["gcjs_fangjianshizheng_zhongbiao_fw_gg", "http://ggzy.njzwfw.gov.cn/njweb/fjsz/068003/068003001/moreinfo3.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "房建市政","type":"服务"}), f2],
    ["gcjs_fangjianshizheng_zhongbiao_gc_gg", "http://ggzy.njzwfw.gov.cn/njweb/fjsz/068003/068003002/moreinfo3.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "房建市政","type":"工程"}), f2],
    ["gcjs_fangjianshizheng_zhongbiao_xxgc_gg", "http://ggzy.njzwfw.gov.cn/njweb/fjsz/068003/068003003/moreinfo4b.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "房建市政","type":"小型工程"}), f2],
    #
    ["gcjs_fangjianshizheng_liubiao_gg", "http://ggzy.njzwfw.gov.cn/njweb/fjsz/068005/068005003/moreinfo5d.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "房建市政"}), f2],
    ["gcjs_fangjianshizheng_zgysjg_gg", "http://ggzy.njzwfw.gov.cn/njweb/fjsz/068005/068005004/moreinfo5d.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "房建市政"}), f2],
    # # 工程货物
    ["gcjs_gongchenghuowu_zhaobiao_gg", "http://ggzy.njzwfw.gov.cn/njweb/gchw/070001/moreinfogchw.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "工程货物"}), f2],
    ["gcjs_gongchenghuowu_zhongbiaohx_gg", "http://ggzy.njzwfw.gov.cn/njweb/gchw/070003/moreinfogchw.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "工程货物"}), f2],
    ["gcjs_gongchenghuowu_zhongbiao_gg", "http://ggzy.njzwfw.gov.cn/njweb/gchw/070004/moreinfogchw.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "工程货物"}), f2],
    # # # 交通水利
    ["gcjs_jiaotong_zhaobiao_sg_gg", "http://ggzy.njzwfw.gov.cn/njweb/jtsw/069001/069001001/moreinfo5d.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "施工"}), f2],
    ["gcjs_jiaotong_zhaobiao_jl_gg", "http://ggzy.njzwfw.gov.cn/njweb/jtsw/069001/069001002/moreinfo5d.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "监理"}), f2],
    ["gcjs_jiaotong_zhaobiao_kcsj_gg", "http://ggzy.njzwfw.gov.cn/njweb/jtsw/069001/069001003/moreinfo5d.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "勘察设计"}), f2],
    ["gcjs_jiaotong_zhaobiao_clcg_gg", "http://ggzy.njzwfw.gov.cn/njweb/jtsw/069001/069001004/moreinfo5d.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "材料采购"}), f2],
    ["gcjs_jiaotong_zhaobiao_syjc_gg", "http://ggzy.njzwfw.gov.cn/njweb/jtsw/069001/069001005/moreinfo5d.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "试验检测"}), f2],

    ["gcjs_jiaotong_zhongbiao_gg", "http://ggzy.njzwfw.gov.cn/njweb/jtsw/069003/moreinfo5d.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_shuili_zhaobiao_gc_gg", "http://ggzy.njzwfw.gov.cn/njweb/jtsw/069005/069005001/moreinfosl.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "工程"}), f2],
    ["gcjs_shuili_zhaobiao_fw_gg", "http://ggzy.njzwfw.gov.cn/njweb/jtsw/069005/069005002/moreinfosl.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "服务"}), f2],
    ["gcjs_shuili_zhaobiao_hw_gg", "http://ggzy.njzwfw.gov.cn/njweb/jtsw/069005/069005003/moreinfosl.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "货物"}), f2],
    ["gcjs_shuili_zhongbiao_gc_gg", "http://ggzy.njzwfw.gov.cn/njweb/jtsw/069006/069006001/moreinfosl2.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "工程"}), f2],
    ["gcjs_shuili_zhongbiao_fw_gg", "http://ggzy.njzwfw.gov.cn/njweb/jtsw/069006/069006002/moreinfosl2.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "服务"}), f2],
    ["gcjs_shuili_zhongbiao_hw_gg", "http://ggzy.njzwfw.gov.cn/njweb/jtsw/069006/069006003/moreinfosl2.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "货物"}), f2],
    #
    #
    ["gcjs_tielu_zhaobiao_gc_gg", "http://ggzy.njzwfw.gov.cn/njweb/tlhy/073001/073001001/moreinfo5d.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "工程"}), f2],
    ["gcjs_tielu_zhaobiao_fw_gg", "http://ggzy.njzwfw.gov.cn/njweb/tlhy/073001/073001002/moreinfo5d.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "服务"}), f2],
    ["gcjs_tielu_zhaobiao_hw_gg", "http://ggzy.njzwfw.gov.cn/njweb/tlhy/073001/073001003/moreinfo5d.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "货物"}), f2],
    ["gcjs_tielu_zhongbiao_gc_gg", "http://ggzy.njzwfw.gov.cn/njweb/tlhy/073002/073002001/moreinfo5d.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "工程"}), f2],
    ["gcjs_tielu_zhongbiao_fw_gg", "http://ggzy.njzwfw.gov.cn/njweb/tlhy/073002/073002002/moreinfo5d.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "服务"}), f2],
    ["gcjs_tielu_zhongbiao_hw_gg", "http://ggzy.njzwfw.gov.cn/njweb/tlhy/073002/073002003/moreinfo5d.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "货物"}), f2],

    # 政府采购
    # 特殊页面
    #
    ["zfcg_zhaobiao_gg", "http://ggzy.njzwfw.gov.cn/njweb/zfcg/067001/067001001/moreinfozfcg.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg", "http://ggzy.njzwfw.gov.cn/njweb/zfcg/067001/067001002/moreinfozfcg.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    # ["zfcg_zgysjg_gg", "http://ggzy.njzwfw.gov.cn/njweb/zfcg/067003/moreinfozfcg2.html",
    #  ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg", "http://ggzy.njzwfw.gov.cn/njweb/zfcg/067002/067002001/moreinfozfcg2.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg", "http://ggzy.njzwfw.gov.cn/njweb/zfcg/067002/067002002/moreinfozfcg2.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **kwargs):
    est_meta(conp, data=data, diqu="江苏省南京市", **kwargs)
    est_html(conp, f=f3, **kwargs)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "jiangsu", "nanjing"]
    work(conp)
    # driver= webdriver.Chrome()
    # driver.get('http://ggzy.njzwfw.gov.cn/njweb/fjsz/068001/068001002/moreinfo.html')
    # df=f1(driver,632)
    # driver.quit()