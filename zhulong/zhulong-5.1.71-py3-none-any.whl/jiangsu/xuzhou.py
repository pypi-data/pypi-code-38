import re

from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong.util.etl import est_html, est_meta, add_info
import time
_name_="xuzhou"
def f1(driver, num):
    if "MoreinfoZbrgg" in driver.current_url:
        locator = (By.XPATH, '//table[@id="moreinfoListZB1_DataGrid1"]/tbody/tr[1]/td/a')
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        cnum = int(driver.find_element_by_id("moreinfoListZB1_lblCurrent").text)
        val = driver.find_element_by_xpath('//*[@id="moreinfoListZB1_DataGrid1"]/tbody/tr[1]/td[2]/a').get_attribute("href")[-40:]

        while num != cnum:
            if num > cnum:
                driver.find_element_by_id("moreinfoListZB1_lbtnDown").click()
            else:
                driver.find_element_by_id("moreinfoListZB1_lbntUp").click()
            locator = (By.XPATH, "//table//tr[1]/td[@valign='middle']")
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
            cnum = int(driver.find_element_by_id("moreinfoListZB1_lblCurrent").text)
            locator = (
            By.XPATH, '//*[@id="moreinfoListZB1_DataGrid1"]/tbody/tr[1]/td[2]/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

        page = driver.page_source
        body = etree.HTML(page)
        content_list = body.xpath('//table[@id="moreinfoListZB1_DataGrid1"]/tbody/tr')
    else:
        locator = (By.XPATH, "//table//tr[1]/td[@valign='middle']")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        val = driver.find_element_by_xpath('//table[@id="MoreinfoListJyxx1_DataGrid1"]/tbody/tr[1]/td/a').get_attribute("href")[-40:]
        cnum = driver.find_element_by_xpath('//*[@id="MoreinfoListJyxx1_Pager"]/table/tbody/tr/td[1]/font[3]/b').text
        if int(cnum) != int(num):
            driver.execute_script("javascript:__doPostBack('MoreinfoListJyxx1$Pager','{}')".format(num))
            locator = (By.XPATH, "//table//tr[1]/td[@valign='middle']")
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
            locator = (
                By.XPATH, "//table[@id='MoreinfoListJyxx1_DataGrid1']/tbody/tr[1]/td/a[not(contains(@href,'%s'))]" % val)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

        page = driver.page_source
        body = etree.HTML(page)
        content_list = body.xpath('//td[@id="MoreinfoListJyxx1_tdcontent"]//tr')

    data = []
    for content in content_list:
        name = content.xpath("./td/a")[0].text
        if name == '':
            name = '此网站此项无值。'
        new_url = "http://www.xzcet.com" + content.xpath("./td/a/@href")[0]
        ggstart_time = content.xpath("./td")[-1].text.strip()
        temp = [name, ggstart_time, new_url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//table//tr[1]/td[@valign='middle']")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    if "MoreinfoZbrgg" in driver.current_url:
        total_page = driver.find_element_by_xpath('//span[@id="moreinfoListZB1_lblTotal"]').text
    else:
        total_page = driver.find_element_by_xpath(
            '//div[@id="MoreinfoListJyxx1_Pager"]/table/tbody/tr/td[1]/font[2]/b').text

    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@align='center']//tr[@align='center']")
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

    div = soup.find('table', runat='server')
    return div

def work(conp,**kwargs):
    est_meta(conp, data=data, diqu="江苏省徐州市",**kwargs)
    est_html(conp, f=f3,**kwargs)

data=[
    # 工程建设招标
    ["gcjs_zhaobiao_gg", "http://www.xzcet.com/xzwebnew/ztbpages/MoreinfoZbgg.aspx?categoryNum=046001",
     ["name", "ggstart_time", "href","info"], f1, f2],

    # # 工程建设最高价
    ["gcjs_kongzhijia_gg", "http://www.xzcet.com/xzwebnew/ztbpages/MoreinfoZgxjgs.aspx?categoryNum=046003",
     ["name", "ggstart_time", "href","info"], f1, f2],

    # 工程建设候选人
    ["gcjs_zhongbiaohx_gg", "http://www.xzcet.com/xzwebnew/ztbpages/MoreinfoZbhxrgs.aspx?categoryNum=046004",
     ["name", "ggstart_time", "href","info"], f1, f2],


    # 工程建设中标  特殊
    ["gcjs_zhongbiao_gg", "http://www.xzcet.com/xzwebnew/ztbpages/MoreinfoZbrgg.aspx?categoryNum=046002",
     ["name", "ggstart_time", "href","info"], f1, f2],

    # 工程建设未入围
    ["gcjs_zgysjg_gg", "http://www.xzcet.com/xzwebnew/ztbpages/MoreInfoWrwgs.aspx?categoryNum=046005",
     ["name", "ggstart_time", "href","info"], f1, f2],

]


if __name__ == "__main__":
    conp=["postgres", "since2015", "192.168.3.171", "jiangsu", "xuzhou"]
    import sys
    arg=sys.argv
    if len(arg) >3:
        work(conp,num=int(arg[1]),total=int(arg[2]),html_total=int(arg[3]))
    elif len(arg) == 2:
        work(conp, html_total=int(arg[1]))
    else:
        work(conp)
    # url = "http://www.xzcet.com/xzwebnew/ztbpages/MoreinfoZbrgg.aspx?categoryNum=046002"
    # for i in range(2,500):
    #     d = webdriver.Chrome()
    #     d.get(url)
    #     f1(d,i)
    #     d.quit()
