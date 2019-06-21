import json
import math
import time

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from zhulong.util.etl import est_tbs, est_meta, est_html, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]

#
# url="http://www.cqyc.gov.cn/ztzl/ggzyjyzx/zfcg/cgjggg/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_ = 'chongqing'


def f1(driver, num):

    locator = (By.XPATH, "//body/pre[string-length()>200]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = int(re.findall(r'&pageIndex=(\d+)&', url)[0])

    if num != cnum:
        url = re.sub(r"&pageIndex=\d+&", "&pageIndex=%s&" % num, url)

        val = len(driver.page_source)

        driver.get(url)
        locator = (By.XPATH, "//body/pre[string-length()>200]")

        WebDriverWait(
            driver, 10).until(
            lambda driver: len(driver.page_source) != val and EC.presence_of_element_located(locator))
        time.sleep(0.5)

    data = []

    content=driver.page_source.replace('\\','')
    contents=re.findall('\{"return":"\[(.+)\]"\}',content)[0]
    cons=re.findall('\{(.+?)\}',contents)
    for c in cons:

        name=re.findall('"title":"(.+?)"',c)[0]
        ggstart_time=re.findall('"infodate":"(.+?)"',c)[0]
        href=re.findall('"infourl":"(.+?)"',c)[0]
        diqu=re.findall('"infoC":"(.+?)"',c)

        diqu=diqu[0] if diqu else None

        info = json.dumps({'diqu':diqu},ensure_ascii=False)

        if 'http' in href:
            href=href
        else:
            href='https://www.cqggzy.com'+href
        tmp = [name, ggstart_time, href,info]

        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, "//body/pre[string-length()>200]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url=driver.current_url
    url=re.sub('getInfoList\?response=application/json&pageIndex=\d+&pageSize=\d+&','getInfoListCount?response=application/json&',url)
    driver.get(url)
    locator = (By.XPATH, "//body/pre[contains(string(),'return')]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total=driver.find_element_by_xpath('//body/pre').text
    total=re.findall('{"return":(\d+)}',total)[0]

    total=math.ceil(int(total)/18)

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@id="mainContent"][string-length()>50]')

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

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_='detail-block')
    return div


data = [

    ["gcjs_zhaobiao_gg",
     "https://www.cqggzy.com/webservice/services/PortalsWebservice/getInfoList?response=application/json&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014001001&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],

    ["gcjs_zhaobiao_yaoqing_gg",
     "https://www.cqggzy.com/webservice/services/PortalsWebservice/getInfoList?response=application/json&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014001014&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], add_info(f1,{"zbfs":'邀请招标'}), f2],

    ["gcjs_gqita_da_bian_gg",
     "https://www.cqggzy.com/webservice/services/PortalsWebservice/getInfoList?response=application/json&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014001002&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],

   [ "gcjs_gqita_richeng_gg",
     "https://www.cqggzy.com/webservice/services/PortalsWebservice/getInfoList?response=application/json&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014001015&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], add_info(f1,{"jytype":'日程安排'}), f2],

    ["gcjs_zhongbiaohx_gg",
     "https://www.cqggzy.com/webservice/services/PortalsWebservice/getInfoList?response=application/json&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014001003&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],
    ["gcjs_zhongbiao_gg",
     "https://www.cqggzy.com/webservice/services/PortalsWebservice/getInfoList?response=application/json&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014001004&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],
    ["gcjs_liubiao_gg",
     "https://www.cqggzy.com/webservice/services/PortalsWebservice/getInfoList?response=application/json&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014001016&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],

    ["zfcg_zhaobiao_gg",
     "https://www.cqggzy.com/webservice/services/PortalsWebservice/getInfoList?response=application/json&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014005001&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],
    ["zfcg_gqita_da_bian_gg",
     "https://www.cqggzy.com/webservice/services/PortalsWebservice/getInfoList?response=application/json&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014005002&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],
    ["zfcg_zhongbiaohx_gg",
     "https://www.cqggzy.com/webservice/services/PortalsWebservice/getInfoList?response=application/json&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014005003&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],
    ["zfcg_zhongbiao_gg",
     "https://www.cqggzy.com/webservice/services/PortalsWebservice/getInfoList?response=application/json&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014005004&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],
    ["zfcg_yucai_gg",
     "https://www.cqggzy.com/webservice/services/PortalsWebservice/getInfoList?response=application/json&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014005008&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],

    ["qsy_zhaobiao_gg",
     "https://www.cqggzy.com/webservice/services/PortalsWebservice/getInfoList?response=application/json&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014008001&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],
    ["qsy_gqita_da_bian_gg",
     "https://www.cqggzy.com/webservice/services/PortalsWebservice/getInfoList?response=application/json&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014008002&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],
    ["qsy_zhongbiaohx_gg",
     "https://www.cqggzy.com/webservice/services/PortalsWebservice/getInfoList?response=application/json&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014008003&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],

    ["jqita_zhaobiao_gg",
     "https://www.cqggzy.com/webservice/services/PortalsWebservice/getInfoList?response=application/json&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014003001&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], add_info(f1,{'tag':'机电设备'}), f2],
    ["jqita_gqita_da_bian_gg",
     "https://www.cqggzy.com/webservice/services/PortalsWebservice/getInfoList?response=application/json&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014003002&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], add_info(f1,{'tag':'机电设备'}), f2],
    ["jqita_gqita_da_bian_gg",
     "https://www.cqggzy.com/webservice/services/PortalsWebservice/getInfoList?response=application/json&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014003004&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], add_info(f1,{'tag':'机电设备'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="重庆市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':

    conp = ["postgres", "since2015", "192.168.3.171", "chongqing", "chongqing"]

    work(conp=conp,num=1,total=2,headless=True)
