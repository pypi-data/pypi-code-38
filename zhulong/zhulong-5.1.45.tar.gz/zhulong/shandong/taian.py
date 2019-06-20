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
from zhulong.util.etl import gg_html, gg_meta, est_tables, est_html, est_meta, add_info

_name_='taian'


def f1(driver, num):
    url= driver.current_url
    locator = (By.XPATH, '//*[@id="right_table"]/table/tbody/tr[1]/td[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//td[@class='huifont']")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.split('/')[0]
    except:
        cnum =1
    if num != int(cnum):
        if "?Paging" not in url:
            s = "?Paging=%d" % (num) if num > 1 else "?Paging=1"
            url = url + s
        elif num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
        val = driver.find_element_by_xpath('//*[@id="right_table"]/table/tbody/tr[1]/td[2]/a').get_attribute('href')[-35:]
        driver.get(url)
        locator = (By.XPATH, "//*[@id='right_table']/table/tbody/tr[1]/td[2]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '(//a[@class="WebList_sub"])[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    html_data = driver.page_source
    soup = BeautifulSoup(html_data, 'html.parser')
    ul = soup.find("div", id="right_table")
    lis = ul.find_all("tr", height='30')
    data = []
    for li in lis:
        a = li.find("a")
        try:
            title = a["title"]
        except:
            title = a.text.strip()
        link = "http://www.taggzyjy.com.cn" + a["href"]
        span = li.find("td", width='80').text.strip()
        span_1 = re.findall(r"\[(.*)\]", span)[0]
        tmp = [title, span_1, link]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df




def f2(driver):
    if ('本栏目信息正在更新中' in driver.page_source) or ('404' in driver.title):
        return 0
    locator = (By.ID, "right_table")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//td[@class='huifont']")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    txt=driver.find_element_by_xpath("//td[@class='huifont'][contains(string(),'/')]").text
    total=txt.split("/")[1]
    total=int(total)
    driver.quit()
    return total




def f3(driver,url):
    driver.get(url)
    locator=(By.XPATH,"//div[@class='inner'][string-length()>30]")
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
    div=soup.find('div',class_='inner')
    td=div.find("td",width="998")
    return td


data = [
        #工程建设-招标公告
        ["gcjs_zhaobiao_diqu1_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001001/075001001001/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"市本级"}),f2],

        ["gcjs_zhaobiao_diqu21_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001001/075001001002/075001001002001/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"市-泰山区"}),f2],


        ["gcjs_zhaobiao_diqu22_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001001/075001001002/075001001002002/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"市-高新区"}),f2],


        ["gcjs_zhaobiao_diqu23_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001001/075001001002/075001001002003/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"市-泰山景区"}),f2],

        ["gcjs_zhaobiao_diqu3_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001001/075001001004/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"新泰市"}),f2],

        ["gcjs_zhaobiao_diqu4_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001001/075001001005/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"肥城市"}),f2],

        ["gcjs_zhaobiao_diqu5_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001001/075001001006/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"宁阳县"}),f2],

        ["gcjs_zhaobiao_diqu6_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001001/075001001007/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"东平县"}),f2],

        ["gcjs_zhaobiao_diqu7_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001001/075001001008/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"岱岳区"}),f2],


         #工程建设-中标候选人
        ["gcjs_zhongbiaohx_diqu1_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001002/075001002001/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"市本级"}),f2],

        ["gcjs_zhongbiaohx_diqu21_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001002/075001002002/075001002002001/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"市-泰山区"}),f2],

        ["gcjs_zhongbiaohx_diqu22_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001002/075001002002/075001002002002/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"市-高新区"}),f2],

        ["gcjs_zhongbiaohx_diqu23_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001002/075001002002/075001002002003/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"市-泰山景区"}),f2],

        ["gcjs_zhongbiaohx_diqu3_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001002/075001002004/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"新泰市"}),f2],

        ["gcjs_zhongbiaohx_diqu4_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001002/075001002005/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"肥城市"}),f2],

        ["gcjs_zhongbiaohx_diqu5_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001002/075001002006/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"宁阳县"}),f2],

        ["gcjs_zhongbiaohx_diqu6_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001002/075001002007/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"东平县"}),f2],

        ["gcjs_zhongbiaohx_diqu7_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001002/075001002008/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"岱岳区"}),f2],


         #工程建设变更公告
        ["gcjs_biangeng_diqu1_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001003/075001003001/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"市本级"}),f2],

        # ["gcjs_biangeng_diqu21_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001003/075001003002/075001003002001/",
        #  ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"市-泰山区"}),f2],

        ["gcjs_biangeng_diqu22_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001003/075001003002/075001003002002/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"市-高新区"}),f2],

        # ["gcjs_biangeng_diqu23_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001003/075001003002/075001003002003/",
        #  ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"市-泰山景区"}),f2],

        ["gcjs_biangeng_diqu3_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001003/075001003004/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"新泰市"}),f2],

        ["gcjs_biangeng_diqu4_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001003/075001003005/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"肥城市"}),f2],

        ["gcjs_biangeng_diqu5_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001003/075001003006/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"宁阳县"}),f2],

        ["gcjs_biangeng_diqu6_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001003/075001003007/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"东平县"}),f2],

        ["gcjs_biangeng_diqu7_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001003/075001003008/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"岱岳区"}),f2],
        #
        # 工程建设-中标公告
        ["gcjs_zhongbiao_diqu1_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001004/075001004001/",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {"diqu": "市本级"}), f2],

        ["gcjs_zhongbiao_diqu21_gg",
         "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001004/075001004002/075001004002001/",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {"diqu": "市-泰山区"}), f2],

        ["gcjs_zhongbiao_diqu22_gg",
         "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001004/075001004002/075001004002002/",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {"diqu": "市-高新区"}), f2],

        ["gcjs_zhongbiao_diqu23_gg",
         "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001004/075001004002/075001004002003/",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {"diqu": "市-泰山景区"}), f2],

        ["gcjs_zhongbiao_diqu3_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001004/075001004003/",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {"diqu": "岱岳区"}), f2],

        ["gcjs_zhongbiao_diqu4_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001004/075001004004/",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {"diqu": "新泰市"}), f2],
        #
        ["gcjs_zhongbiao_diqu5_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001004/075001004005/",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {"diqu": "肥城市"}), f2],
        #
        ["gcjs_zhongbiao_diqu6_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001004/075001004006/",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {"diqu": "宁阳县"}), f2],
        #
        ["gcjs_zhongbiao_diqu7_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075001/075001004/075001004007/",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {"diqu": "东平县"}), f2],

        #
        #政府采购-需求公开
        ["zfcg_yucai_diqu1_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002004/075002004001/",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {"diqu": "市本级"}), f2],

        ["zfcg_yucai_diqu21_gg",
         "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002004/075002004002/075002004002001/",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {"diqu": "市-泰山区"}), f2],

        ["zfcg_yucai_diqu22_gg",
         "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002004/075002004002/075002004002002/",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {"diqu": "市-泰山景区"}), f2],

        ["zfcg_yucai_diqu23_gg",
         "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002004/075002004002/075002004002003/",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {"diqu": "市-高新区"}), f2],

        ["zfcg_yucai_diqu3_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002004/075002004003/",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {"diqu": "岱岳区"}), f2],

        ["zfcg_yucai_diqu4_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002004/075002004004/",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {"diqu": "新泰市"}), f2],
        #
        ["zfcg_yucai_diqu5_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002004/075002004005/",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {"diqu": "肥城市"}), f2],
        #
        ["zfcg_yucai_diqu6_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002004/075002004006/",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {"diqu": "宁阳县"}), f2],
        #
        ["zfcg_yucai_diqu7_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002004/075002004007/",
         ["name", "ggstart_time", "href", "info"], add_info(f1, {"diqu": "东平县"}), f2],

         #政府采购-招标公告
        ["zfcg_zhaobiao_diqu1_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002001/075002001001/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"市本级"}),f2],


        ["zfcg_zhaobiao_diqu21_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002001/075002001002/075002001002001/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"市-泰山区"}),f2],

        ["zfcg_zhaobiao_diqu22_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002001/075002001002/075002001002003/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"市-高新区"}),f2],

        ["zfcg_zhaobiao_diqu23_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002001/075002001002/075002001002004/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"市-泰山景区"}),f2],

        ["zfcg_zhaobiao_diqu3_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002001/075002001004/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"新泰市"}),f2],

        ["zfcg_zhaobiao_diqu4_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002001/075002001005/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"肥城市"}),f2],

        ["zfcg_zhaobiao_diqu5_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002001/075002001006/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"宁阳县"}),f2],

        ["zfcg_zhaobiao_diqu6_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002001/075002001007/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"东平县"}),f2],

        ["zfcg_zhaobiao_diqu7_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002001/075002001008/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"岱岳区"}),f2],


         #政府采购-中标标公告
        ["zfcg_zhongbiaohx_diqu1_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002002/075002002001/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"市本级"}),f2],


        ["zfcg_zhongbiaohx_diqu21_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002002/075002002002/075002002002001/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"市-泰山区"}),f2],

        ["zfcg_zhongbiaohx_diqu22_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002002/075002002002/075002002002003/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"市-高新区"}),f2],

        ["zfcg_zhongbiaohx_diqu23_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002002/075002002002/075002002002004/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"市-泰山景区"}),f2],

        ["zfcg_zhongbiaohx_diqu3_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002002/075002002004/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"新泰市"}),f2],

        ["zfcg_zhongbiaohx_diqu4_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002002/075002002005/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"肥城市"}),f2],

        ["zfcg_zhongbiaohx_diqu5_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002002/075002002006/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"宁阳县"}),f2],

        ["zfcg_zhongbiaohx_diqu6_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002002/075002002007/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"东平县"}),f2],

        ["zfcg_zhongbiaohx_diqu7_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002002/075002002008/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"岱岳区"}),f2],


         #政府采购-变更公告
        ["zfcg_biangeng_diqu1_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002003/075002003001/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"市本级"}),f2],


        ["zfcg_biangeng_diqu21_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002003/075002003002/075002003002001/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"市-泰山区"}),f2],

        ["zfcg_biangeng_diqu22_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002003/075002003002/075002003002003/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"市-高新区"}),f2],

        ["zfcg_biangeng_diqu23_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002003/075002003002/075002003002004/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"市-泰山景区"}),f2],

        ["zfcg_biangeng_diqu3_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002003/075002003004/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"新泰市"}),f2],

        ["zfcg_biangeng_diqu4_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002003/075002003005/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"肥城市"}),f2],

        ["zfcg_biangeng_diqu5_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002003/075002003006/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"宁阳县"}),f2],

        ["zfcg_biangeng_diqu6_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002003/075002003007/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"东平县"}),f2],

        ["zfcg_biangeng_diqu7_gg", "http://www.taggzyjy.com.cn/Front/jyxx/075002/075002003/075002003008/",
         ["name", "ggstart_time", "href","info"],add_info(f1,{"diqu":"岱岳区"}),f2],

    ]




def work(conp,**args):
    est_meta(conp,data=data,diqu="山东省泰安市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shandong","taian"])


