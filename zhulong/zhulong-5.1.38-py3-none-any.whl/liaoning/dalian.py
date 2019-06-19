import re

from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong.util.etl import est_html,est_meta
import time

_name_="dalian"
def f1(driver, num):
    if "071002" in driver.current_url or "071001" in driver.current_url:   # 同一种网站，两个框架
        locator = (By.XPATH, '//*[@id="categorypagingcontent"]/div/table/tbody/tr[1]/td[2]/a')
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        val = driver.find_element_by_xpath('//*[@id="categorypagingcontent"]/div/table/tbody/tr[1]/td[2]/a').get_attribute("href")[-50:]
        locator = (By.ID, "categorypagingcontent")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        cnum = driver.find_element_by_xpath('//li[@class="ewb-page-li ewb-page-noborder ewb-page-num"]/span').text.split("/")[0]
        if int(cnum) != int(num):
            driver.execute_script("ShowAjaxNewPage(window.location.pathname,'categorypagingcontent',{})".format(num))
            locator = (By.XPATH, '//*[@id="categorypagingcontent"]/div/table/tbody/tr[1]/td[2]/a')
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
            locator = (
                By.XPATH, "//*[@id='categorypagingcontent']/div/table/tbody/tr[1]/td[2]/a[not(contains(@href,'%s'))]" % val)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        page = driver.page_source
        body = etree.HTML(page)
        content_list = body.xpath('//table[@class="ewb-trade-tb"]/tbody/tr')
        data = []
        for content in content_list:
            try:
                name = content.xpath("./td/a")[0].xpath("string(.)").strip()
            except:
                name = 'None'
            new_url = "http://ggzyjy.dl.gov.cn" + content.xpath("./td/a/@href")[0].strip()
            ggstart_time = content.xpath("./td[4]/text()")[0].strip()
            temp = [name, ggstart_time, new_url]
            data.append(temp)
    else:
        locator = (By.XPATH, '//*[@id="categorypagingcontent"]/div/ul/li[1]/div/a')
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        val = driver.find_element_by_xpath('//*[@id="categorypagingcontent"]/div/ul/li[1]/div/a').get_attribute("href")[-50:]
        # print(val)
        try:
            locator = (By.ID, "categorypagingcontent")
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
            cnum = \
            driver.find_element_by_xpath('//li[@class="ewb-page-li ewb-page-noborder ewb-page-num"]/span').text.split("/")[0]
        except:
            cnum = 1
        if int(cnum) != int(num): #ShowAjaxNewPage(window.location.pathname,'categorypagingcontent',3)
            driver.execute_script("ShowAjaxNewPage(window.location.pathname,'categorypagingcontent',{})".format(num))
            locator = (By.XPATH, '//*[@id="categorypagingcontent"]/div/ul/li[1]/div/a')
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
            locator = (
                By.XPATH,
                "//*[@id='categorypagingcontent']/div/ul/li[1]/div/a[not(contains(@href,'%s'))]" % val)
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        page = driver.page_source
        body = etree.HTML(page)
        content_list = body.xpath('//div[@class="categorypagingcontent"]/ul/li')
        data = []
        for content in content_list:
            name = content.xpath("./div/a/text()")[0].strip()
            new_url = "http://ggzyjy.dl.gov.cn" + content.xpath("./div/a/@href")[0].strip()
            ggstart_time = content.xpath("./span/text()")[0].strip()
            temp = [name, ggstart_time, new_url]
            data.append(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df



def f2(driver):

    try:
        locator = (By.ID, "categorypagingcontent")
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
        total_page = driver.find_element_by_xpath('//li[@class="ewb-page-li ewb-page-noborder ewb-page-num"]/span').text.split("/")[1]
    except:
        total_page = 1


    driver.quit()
    # print(total_page)
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    if "ewb-container" in driver.page_source:
        locator = (By.CLASS_NAME, "ewb-container")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag=True
    elif "tblInfo" in driver.page_source:
        locator = (By.ID, "tblInfo")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag=False
    else:
        locator = (By.ID, "ewb-main")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag=3
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
    if flag == True:
        div = soup.find('div', class_='ewb-container')
    elif flag == 3:
        div = soup.find("div",class_='ewb-main')
    else:
        div = soup.find('table', id='tblInfo')
    return div





data = [
    # 公共资源
    ["gcjs_zhaobiao_gg",
     "http://ggzyjy.dl.gov.cn/TPFront/jyxx/071001/071001001/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://ggzyjy.dl.gov.cn/TPFront/jyxx/071001/071001002/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://ggzyjy.dl.gov.cn/TPFront/jyxx/071001/071001003/",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["zfcg_gqita_zhao_bian_gg",
     "http://ggzyjy.dl.gov.cn/TPFront/jyxx/071002/071002001/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://ggzyjy.dl.gov.cn/TPFront/jyxx/071002/071002003/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_dyly_gg",
     "http://ggzyjy.dl.gov.cn/TPFront/jyxx/071002/071002005/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_shuiyun_zhaobiao_gg",
     "http://ggzyjy.dl.gov.cn/TPFront/jyxx/071006/071006001/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuiyun_zhongbiaohx_gg",
     "http://ggzyjy.dl.gov.cn/TPFront/jyxx/071006/071006002/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuiyun_zhongbiao_gg",
     "http://ggzyjy.dl.gov.cn/TPFront/jyxx/071006/071006003/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_gonglu_zhao_bian_gg",
     "http://ggzyjy.dl.gov.cn/TPFront/jyxx/071007/071007001/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gonglu_zhongbiaohx_gg",
     "http://ggzyjy.dl.gov.cn/TPFront/jyxx/071007/071007002/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gonglu_zhongbiao_gg",
     "http://ggzyjy.dl.gov.cn/TPFront/jyxx/071007/071007003/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #


    ["yiliao_gqita_zhao_bian_liu_gg",
     "http://ggzyjy.dl.gov.cn/TPFront/jyxx/071008/071008001/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["yiliao_zhongbiao_gg",
     "http://ggzyjy.dl.gov.cn/TPFront/jyxx/071008/071008003/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["yiliao_zhaobiao_dyly_gg",
     "http://ggzyjy.dl.gov.cn/TPFront/jyxx/071008/071008005/",
     ["name", "ggstart_time", "href", "info"], f1, f2],



    ["gcjs_shuili_zhaobiao_gg",
     "http://ggzyjy.dl.gov.cn/TPFrontNew/jyxx/071009/071009001/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuili_zhongbiaohx_gg",
     "http://ggzyjy.dl.gov.cn/TPFront/jyxx/071009/071009002/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuili_zhongbiao_gg",
     "http://ggzyjy.dl.gov.cn/TPFront/jyxx/071009/071009003/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp,**arg):
    est_meta(conp, data=data, diqu="辽宁省大连市",**arg)
    est_html(conp, f=f3,**arg)

if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "liaoning", "dalian"])
    # url = "http://ggzyjy.dl.gov.cn/TPFront/jyxx/071002/071002001/"
    # driver= webdriver.Chrome()
    # driver.get(url)
    # for i in range(800,1000):
    #     f1(driver,i)


