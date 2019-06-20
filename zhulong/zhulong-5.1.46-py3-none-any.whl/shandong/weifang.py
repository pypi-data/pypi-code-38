import time
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
import json
from zhulong.util.etl import est_tables, gg_meta, gg_html, est_meta, est_html, add_info

_name_='weifang'


def f1(driver, num):
    locator = (By.XPATH, '(//span[@class="info-name"])[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    # print(url)
    locator = (By.XPATH, '//td[@class="huifont"]')
    page_all = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall('(\d+)/', page_all)[0]
    if num != int(cnum):
        if num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
        val = driver.find_element_by_xpath("(//span[@class='info-name']/a)[1]").get_attribute('href')[-36:]
        driver.get(url)
        locator = (By.XPATH, "(//span[@class='info-name']/a)[1][not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    ul = soup.find("div", class_="info-form")
    tbody = ul.find('tbody')
    trs = tbody.find_all("tr")
    data = []
    for li in trs:
        try:
            info_number = li.find("span", class_="info-number").text
        except:
            info_number = "-"
        a = li.find("a")
        try:
            title = a['title']
        except:
            title = a.text.strip()
        link = "http://ggzy.weifang.gov.cn" + a["href"]
        try:
            span1 = li.find_all("span", class_="info-date")[0].text
        except:
            span1 = "-"
        try:
            span2 = li.find_all("span", class_="info-date")[1].text
        except:
            span2 = "-"
        tmp = [info_number.strip(), title, span1.strip(), span2.strip(), link]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"]=None
    return df


def f2(driver):
    if ('本栏目暂时没有内容' in driver.page_source) or ('404' in driver.title):
        return 0
    locator = (By.XPATH, '(//span[@class="info-name"])[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, '//td[@class="huifont"]')
    page_all = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    page = re.findall('/(\d+)', page_all)[0]
    driver.quit()
    return int(page)



def f3(driver,url):
    driver.get(url)
    locator=(By.XPATH,"//div[@class='detail-content'][string-length()>30]")
    WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))
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
    div=soup.find('div',class_='detail-content')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg.aspx?address=&type=&categorynum=004012001&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"], f1, f2],

    ["gcjs_biangeng_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg.aspx?address=&type=&categorynum=004012002&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"], f1, f2],

    ["gcjs_gqita_bian_da_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg.aspx?address=&type=&categorynum=004012005&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg.aspx?address=&type=&categorynum=004012006&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg.aspx?address=&type=&categorynum=004012007&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"], f1, f2],

    ["gcjs_liubiao_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_ggycgg.aspx?address=&type=&categorynum=004012010&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_danyilaiyuan_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg.aspx?address=&type=&categorynum=004012008&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"], add_info(f1,{'zbfs':'单一来源'}), f2],

    ["zfcg_yucai_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg_zfcg_cgxq.aspx?address=&categorynum=004002017&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg_zfcg_cgxq.aspx?address=&categorynum=004002001&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg_zfcg.aspx?address=&type=&categorynum=004002011&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg_zfcg.aspx?address=&type=&categorynum=004002012&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"], f1, f2],

    ["zfcg_liubiao_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg_zfcg.aspx?address=&type=&categorynum=004002016&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"], f1, f2],

    ["zfcg_zhongzhi_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg_zfcg.aspx?address=&type=&categorynum=004002015&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"], f1, f2],

    ["zfcg_yanshou_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg_zfcg.aspx?address=&type=&categorynum=004002014&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"], f1, f2],

    ["zfcg_hetong_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg_zfcg.aspx?address=&type=&categorynum=004002013&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"], f1, f2],

    ["yiliao_zhaobiao_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg_ylsb.aspx?address=&categorynum=004006001&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"],add_info(f1,{'jylx':'医疗设备'}), f2],

    ["yiliao_biangeng_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg_ylsb.aspx?address=&categorynum=004006002&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"],add_info(f1,{'jylx':'医疗设备'}), f2],

    ["yiliao_zhongbiao_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg_ylsb.aspx?address=&categorynum=004006003&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"],add_info(f1,{'jylx':'医疗设备'}), f2],

    ["yiliao_yanshou_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg_ylsb.aspx?address=&categorynum=004006007&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"],add_info(f1,{'jylx':'医疗设备'}), f2],

    ["yiliao_liubiao_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg_ylsb.aspx?address=&categorynum=004006008&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"],add_info(f1,{'jylx':'医疗设备'}), f2],

    ["qsy_zhaobiao_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg_ylsb.aspx?address=&categorynum=004007001&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"],add_info(f1,{'jylx':'其他交易'}), f2],

    ["qsy_biangeng_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg_ylsb.aspx?address=&categorynum=004007004&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"],add_info(f1,{'jylx':'其他交易'}), f2],

    ["qsy_zhongbiao_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg_ylsb.aspx?address=&categorynum=004007002&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"],add_info(f1,{'jylx':'其他交易'}), f2],

    ["qsy_zhongzhi_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg_ylsb.aspx?address=&categorynum=004007007&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"],add_info(f1,{'jylx':'其他交易'}), f2],

    ["qsy_liubiao_gg",
     "http://ggzy.weifang.gov.cn/wfggzy/showinfo/moreinfo_gg_ylsb.aspx?address=&categorynum=004007009&Paging=1",
     ["info_number", "name", "ggstart_time", "ggend_time", "href", "info"],add_info(f1,{'jylx':'其他交易'}), f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="山东省潍坊市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shandong","weifang"])

