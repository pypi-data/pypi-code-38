import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_command,db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import json



from zhulong.util.etl import add_info,est_meta,est_html,est_tbs


_name_="linhai"



def f1(driver, num):
    url = driver.current_url
    locator = (By.XPATH, "//td[@align='center' and @valign='top']/table[1]/tbody/tr/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//span[@id='Label1']/div")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = re.findall(r'第(\d+)页', cnum)[0]
    if num != int(cnum):
        val = driver.find_element_by_xpath("//td[@align='center' and @valign='top']/table[1]/tbody/tr/td/a").get_attribute('href')[-30:]
        if '&pageindex=' not in url:
            s = '&pageindex=%d' % num if num > 1 else "&pageindex=1"
            url+=s
        if num == 1:
            url = re.sub("pageindex=[0-9]*", "pageindex=1", url)
        else:
            s = "pageindex=%d" % (num) if num > 1 else "pageindex=1"
            url = re.sub("pageindex=[0-9]*", s, url)
        driver.get(url)
        locator = (By.XPATH, "//td[@align='center' and @valign='top']/table[1]/tbody/tr/td/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("td", align="center", valign="top")
    trs = table.find_all("table")
    data = []
    for tr in trs:
        a = tr.find_all("tr")[0].a
        try:
            title = a["title"].strip()
        except:
            title = a.text.strip()
        td = tr.find("td", width="102").text.strip()
        td = re.findall(r'\[(.*)\]', td)[0]

        link = "http://www.lhztb.gov.cn"+a["href"].strip()
        if '[新]' in title:
            title = re.sub(r'\[新\]', '', title)
        tmp = [title, td, link]
        data.append(tmp)

    df = pd.DataFrame(data)
    df['info'] = None
    return df





def f2(driver):
    locator = (By.XPATH, "//td[@align='center' and @valign='top']/table[1]/tbody/tr/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//span[@id='Label1']/div")
    num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'共(\d+)页', num)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    if '<iframe src="http://www.lhztb.gov' in driver.page_source:
        iframe = driver.find_element_by_xpath('//iframe[@scrolling="yes"]')
        driver.switch_to_frame(iframe)
    locator = (By.XPATH, "//td[@id='RightPane'][string-length()>40]")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    if ('开标记录' in driver.page_source) and ('开标时间：<span id="_ctl3_lblKbDate">Label</span>' in driver.page_source):
        driver.find_element_by_xpath("//table[@class='Lbtbcolor1']//a/font[contains(text(), '开标结果')]").click()
        locator = (By.XPATH, "//td[@id='RightPane'][string-length()>40]")
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
    div = soup.find_all('td', id="RightPane")
    return div




data = [
    ["gcjs_gqita_yuzhaobiao_gg",
     "http://www.lhztb.gov.cn/dahai/viewmore1.aspx?PrjTypeId=01",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'gglx':'项目信息'}),f2],

    ["gcjs_zhaobiao_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=01&BulletinTypeId=11&pageindex=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=01&BulletinTypeId=13",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_kaibiao_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=01&BulletinTypeId=16",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=01&BulletinTypeId=12",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=01&BulletinTypeId=15",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_hetong_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=01&BulletinTypeId=17",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_yanshou_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=01&BulletinTypeId=14",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_yuzhaobiao_gg",
     "http://www.lhztb.gov.cn/dahai/viewmore1.aspx?PrjTypeId=02",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'gglx':'项目信息'}),f2],

    ["zfcg_yucai_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=02&BulletinTypeId=28",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhaobiao_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=02&BulletinTypeId=21",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_gqita_bian_bu_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=02&BulletinTypeId=23",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_kaibiao_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=02&BulletinTypeId=26",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhongbiaohx_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=02&BulletinTypeId=22",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhongbiao_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=02&BulletinTypeId=25",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_hetong_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=02&BulletinTypeId=27",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_yanshou_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=02&BulletinTypeId=24",
     ["name", "ggstart_time", "href", "info"],f1,f2],


    ["gcjs_gqita_yuzhaobiao_xiaoe_gg",
     "http://www.lhztb.gov.cn/dahai/viewmore1.aspx?PrjTypeId=07",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx':'小额工程','gglx':'项目信息'}), f2],

    ["gcjs_zhaobiao_xiaoe_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=07&BulletinTypeId=71",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx':'小额工程'}), f2],

    ["gcjs_gqita_bian_bu_xiaoe_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=07&BulletinTypeId=73",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx':'小额工程'}), f2],

    ["gcjs_kaibiao_xiaoe_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=07&BulletinTypeId=76",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx':'小额工程'}), f2],

    ["gcjs_zhongbiaohx_xiaoe_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=07&BulletinTypeId=72",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx':'小额工程'}), f2],

    ["gcjs_zhongbiao_xiaoe_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=07&BulletinTypeId=75",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx':'小额工程'}), f2],

    ["gcjs_hetong_xiaoe_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=07&BulletinTypeId=77",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': '小额工程'}), f2],

    ["gcjs_gqita_yanshou_xiaoe_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=07&BulletinTypeId=74",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': '小额工程'}), f2],

    ["qsy_gqita_yuzhaobiao_gg",
     "http://www.lhztb.gov.cn/dahai/viewmore1.aspx?PrjTypeId=05",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'自行招标','gglx':'项目信息'}), f2],

    ["qsy_zhaobiao_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=05&BulletinTypeId=51",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx': '自行招标'}), f2],

    ["qsy_gqita_bian_bu_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=05&BulletinTypeId=53",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx': '自行招标'}), f2],

    ["qsy_zhongbiaohx_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=05&BulletinTypeId=52",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx': '自行招标'}), f2],

    ["qsy_zhongbiao_gg",
     "http://www.lhztb.gov.cn/dahai/Bulltinmore1.aspx?PrjTypeId=05&BulletinTypeId=55",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx': '自行招标'}), f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="浙江省临海市",**args)
    est_html(conp,f=f3,**args)


# zfcg_kaibiao_gg、gcjs_kaibiao_gg页数太多，一次性跑不完
if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","zhejiang","linhai"],pageloadtimeout=120)


