import random

import pandas as pd
import re
from lxml import etree
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

from zhulong2.util.etl import est_meta, est_html, add_info

_name_ = 'neimenggu_bayannaoer'


def f3(driver, url):
    driver.get(url)
    time.sleep(random.randint(2, 5))
    locator = (By.XPATH, '//div[@class="newsDetail"]')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
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
    div = soup.find('div', class_='newsDetail')
    return div


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="pageNo J_pageSelect fk-pageSelect"]/span')
    cnum = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text
    if cnum == '':cnum=1
    locator = (By.XPATH, '//div[@topclassname="top1"]/table/tbody/tr/td[2]/a')
    val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')[-25:]

    if int(cnum) != int(num):
        new_url = re.sub('pageno=\d*', 'pageno=' + str(num), driver.current_url)

        driver.get(new_url)

        locator = (By.XPATH, '//div[@topclassname="top1"]/table/tbody/tr/td[2]/a[not(contains(@href,"%s"))]' % val)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    url_part = driver.current_url.split('/')[3]

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@topclassname="top1"]/table/tbody/tr')
    for content in content_list:
        name = content.xpath("./td[2]/a/text()")[0].strip()
        ggstart_time = content.xpath("./td[last()]/a/text()")[0].strip()
        url = "http://www.nmbgp.com/" + content.xpath("./td[2]/a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        #print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    try:
        locator = (By.XPATH, '//div[@class="pageNo"][last()]/a/span')
        total_page = int(WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text)
    except:total_page = 1
    driver.quit()
    return total_page


data = [
    ["zfcg_zhaobiao_gg", "http://www.nmbgp.com/col.jsp?id=107&m315pageno=1", ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '市本级'}),
     f2],
    ["zfcg_biangeng_gg", "http://www.nmbgp.com/col.jsp?id=108&m315pageno=1", ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '市本级'}),
     f2],
    ["zfcg_zhongbiao_gg", "http://www.nmbgp.com/col.jsp?id=109&m317pageno=1", ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '市本级'}),
     f2],
    ["zfcg_liubiao_gg", "http://www.nmbgp.com/col.jsp?id=115&m379pageno=1", ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '市本级'}),
     f2],
    ["zfcg_zhaobiao_kfq_gg", "http://www.nmbgp.com/col.jsp?id=191", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '开发区'}), f2],
    ["zfcg_zhaobiao_tp_kfq_gg", "http://www.nmbgp.com/col.jsp?id=214&m534pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '开发区', 'tag': '竞争性谈判'}), f2],
    ["zfcg_biangeng_zhao_kfq_gg", "http://www.nmbgp.com/col.jsp?id=192", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '开发区', "tag": '招标变更'}), f2],
    ["zfcg_liubiao_kfq_gg", "http://www.nmbgp.com/col.jsp?id=196", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '开发区'}), f2],
    ["zfcg_zhongbiao_gg", "http://www.nmbgp.com/col.jsp?id=194&m522pageno=1", ["name", "ggstart_time", "href", "info"], add_info(f1, {'area': '市本级'}),
     f2],
    ###
    ["zfcg_zhaobiao_lhq_gg", "http://www.nmbgp.com/col.jsp?id=218&m543pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '临河区'}), f2],
    ["zfcg_biangeng_zhao_lhq_gg", "http://www.nmbgp.com/col.jsp?id=219&m544pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '临河区', 'tag': '招标变更'}), f2],
    ["zfcg_biangeng_zhong_lhq_gg", "http://www.nmbgp.com/col.jsp?id=221&m544pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '临河区', 'tag': '中标变更'}), f2],
    ["zfcg_zhongbiao_lhq_gg", "http://www.nmbgp.com/col.jsp?id=220&m545pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '临河区'}), f2],

    ["zfcg_liubiao_lhq_gg", "http://www.nmbgp.com/col.jsp?id=222&m547pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '临河区'}), f2],
    ["zfcg_zgys_lhq_gg", "http://www.nmbgp.com/col.jsp?id=223&m547pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '临河区'}), f2],
    ["zfcg_zhaobiao_tp_lhq_gg", "http://www.nmbgp.com/col.jsp?id=232&m556pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '临河区', 'tag': '竞争性谈判'}), f2],
    ####hjhq

    ["zfcg_zhaobiao_hjhq_gg", "http://www.nmbgp.com/col.jsp?id=234&m562pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '杭锦后旗'}), f2],
    ["zfcg_biangeng_zhao_hjhq_gg", "http://www.nmbgp.com/col.jsp?id=235&m562pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '杭锦后旗', 'tag': '招标变更'}), f2],
    ["zfcg_biangeng_zhong_hjhq_gg", "http://www.nmbgp.com/col.jsp?id=237&m562pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '杭锦后旗', 'tag': '中标变更'}), f2],
    ["zfcg_zhongbiao_hjhq_gg", "http://www.nmbgp.com/col.jsp?id=236&m564pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '杭锦后旗'}), f2],
    ["zfcg_liubiao_hjhq_gg", "http://www.nmbgp.com/col.jsp?id=238&m562pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '杭锦后旗'}), f2],
    ["zfcg_zhaobiao_tp_hjhq_gg", "http://www.nmbgp.com/col.jsp?id=248&m562pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '杭锦后旗', 'tag': '竞争性谈判'}), f2],
    ####dkx

    ["zfcg_zhaobiao_hjhq_gg", "http://www.nmbgp.com/col.jsp?id=250&m581pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '磴口县'}), f2],
    ["zfcg_liubiao_hjhq_gg", "http://www.nmbgp.com/col.jsp?id=254&m581pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '磴口县'}), f2],
    ["zfcg_zhaobiao_cs_hjhq_gg", "http://www.nmbgp.com/col.jsp?id=265&m581pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '磴口县', 'tag': '竞争性磋商'}), f2],
    ####wyx

    ["zfcg_zhaobiao_wyx_gg", "http://www.nmbgp.com/col.jsp?id=266&m600pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '五原县'}), f2],
    ["zfcg_zhongbiao_wyx_gg", "http://www.nmbgp.com/col.jsp?id=268&m602pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '五原县'}), f2],
    ["zfcg_liubiao_wyx_gg", "http://www.nmbgp.com/col.jsp?id=270&m600pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '五原县'}), f2],
    ["zfcg_zhaobiao_tp_wyx_gg", "http://www.nmbgp.com/col.jsp?id=280&m613pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '五原县', 'tag': '竞争性谈判'}), f2],
    ####wltqq

    ["zfcg_zhaobiao_wltqq_gg", "http://www.nmbgp.com/col.jsp?id=282&m620pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '乌拉特前旗'}), f2],
    ["zfcg_zhongbiao_wltqq_gg", "http://www.nmbgp.com/col.jsp?id=284&m622pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '乌拉特前旗'}), f2],
    ["zfcg_liubiao_wltqq_gg", "http://www.nmbgp.com/col.jsp?id=286&m600pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '乌拉特前旗'}), f2],
    ["zfcg_zhaobiao_tp_wltqq_gg", "http://www.nmbgp.com/col.jsp?id=286&m613pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '乌拉特前旗', 'tag': '竞争性谈判'}), f2],
    ####wltzq

    ["zfcg_zhaobiao_wltzq_gg", "http://www.nmbgp.com/col.jsp?id=298&m639pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '乌拉特中旗'}), f2],
    ["zfcg_biangeng_zhao_wltzq_gg", "http://www.nmbgp.com/col.jsp?id=299&m562pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '乌拉特中旗', 'tag': '招标变更'}), f2],

    ["zfcg_zhongbiao_wltzq_gg", "http://www.nmbgp.com/col.jsp?id=300&m641pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '乌拉特中旗'}), f2],
    ["zfcg_biangeng_zhong_wltzq_gg", "http://www.nmbgp.com/col.jsp?id=301&m641pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '乌拉特中旗','tag': '中标变更'}), f2],

    ["zfcg_liubiao_wltzq_gg", "http://www.nmbgp.com/col.jsp?id=302&m643pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '乌拉特中旗'}), f2],

    ["zfcg_zhaobiao_tp_wltzq_gg", "http://www.nmbgp.com/col.jsp?id=312&m652pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '乌拉特中旗', 'tag': '竞争性谈判'}), f2],
    ["zfcg_zhaobiao_yq_wltzq_gg", "http://www.nmbgp.com/col.jsp?id=311&m652pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '乌拉特中旗', 'tag': '邀请招标'}), f2],
    ["zfcg_zhaobiao_cs_wltzq_gg", "http://www.nmbgp.com/col.jsp?id=313&m652pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '乌拉特中旗', 'tag': '竞争性磋商'}), f2],
    ####wlthq

    ["zfcg_zhaobiao_wlthq_gg", "http://www.nmbgp.com/col.jsp?id=314&m658pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '乌拉特后旗'}), f2],
    ["zfcg_biangeng_zhao_wlthq_gg", "http://www.nmbgp.com/col.jsp?id=315&m659pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '乌拉特后旗', 'tag': '招标变更'}), f2],

    ["zfcg_zhongbiao_wlthq_gg", "http://www.nmbgp.com/col.jsp?id=316&m660pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '乌拉特后旗'}), f2],
    ["zfcg_liubiao_wlthq_gg", "http://www.nmbgp.com/col.jsp?id=318&m662pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '乌拉特后旗'}), f2],

    ["zfcg_zhaobiao_tp_wlthq_gg", "http://www.nmbgp.com/col.jsp?id=328&m671pageno=1", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'area': '乌拉特后旗', 'tag': '竞争性谈判'}), f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="内蒙古包彦淖尔市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "neimenggu_bayannaoer"],headless=False,num=2)
    # url = 'http://www.nmbgp.com/col.jsp?id=107&m315pageno=1'
    # driver = webdriver.Chrome()
    # driver.get(url)
    # f1(driver, 3)
