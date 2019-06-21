import re
import time

from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong.util.etl import est_meta,est_html

_name_="liuzhou"
def f1(driver,num):
    locator = (By.XPATH,"//table[@id='JyxxSearch1_DataGrid1']//tr//a")
    WebDriverWait(driver,20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//table[@id='JyxxSearch1_DataGrid1']//tr//a").text

    WebDriverWait(driver,20).until(EC.visibility_of_element_located(locator))
    cnum = driver.find_element_by_xpath("//font[@color='red']").text
    if int(cnum) != int(num):
        driver.execute_script("""javascript:__doPostBack('JyxxSearch1$Pager','%s')"""%num)

        locator = (By.XPATH, '//table[@id="JyxxSearch1_DataGrid1"]//tr//a[not(contains(string(),"%s"))]'%val)
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    page = driver.page_source
    body = etree.HTML(page)
    data = []
    content_list = body.xpath('//table[@id="JyxxSearch1_DataGrid1"]//tr')
    for content in content_list:
        name = content.xpath(".//div/a")[0].xpath("string()")
        ggstart_time = content.xpath("./td/span[last()]/text()")[0].strip()
        url = "http://ggzy.liuzhou.gov.cn" + content.xpath(".//div/a/@href")[0]
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"]=None
    return df


def f2(driver):

    locator = (By.XPATH,"//td[@class='paginator']/font[2]")
    WebDriverWait(driver,20).until(EC.visibility_of_element_located(locator))
    total_page = driver.find_element_by_xpath("//td[@class='paginator']/font[2]").text
    driver.quit()
    return int(total_page)

def f3(driver, url):
    driver.get(url)
    locator = (By.ID, "tblInfo")
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

    div = soup.find('table', id='tblInfo')
    # print(div)
    return div


data =[

    ["gcjs_zhaobiao_gg",
     "http://ggzy.liuzhou.gov.cn/gxlzzbw/showinfo/jyxxmore.aspx?catgorynum1=001&catgorynum2=001&xiaqu=&type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_kongzhijia_gg",
     "http://ggzy.liuzhou.gov.cn/gxlzzbw/showinfo/jyxxmore.aspx?catgorynum1=001&catgorynum2=004&xiaqu=&type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://ggzy.liuzhou.gov.cn/gxlzzbw/showinfo/jyxxmore.aspx?catgorynum1=001&catgorynum2=009&xiaqu=&type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_dayi_gg",
     "http://ggzy.liuzhou.gov.cn/gxlzzbw//showinfo/jyxxmore.aspx?catgorynum1=&catgorynum2=002&xiaqu=&type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://ggzy.liuzhou.gov.cn/gxlzzbw/showinfo/jyxxmore.aspx?catgorynum1=001&catgorynum2=005&xiaqu=&type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_shuili_zhaobiao_gg",
     "http://ggzy.liuzhou.gov.cn/gxlzzbw/showinfo/jyxxmore.aspx?catgorynum1=011&catgorynum2=001&xiaqu=&type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuili_zhongbiaohx_gg",
     "http://ggzy.liuzhou.gov.cn/gxlzzbw/showinfo/jyxxmore.aspx?catgorynum1=011&catgorynum2=002&xiaqu=&type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuili_zhongbiao_gg",
     "http://ggzy.liuzhou.gov.cn/gxlzzbw/showinfo/jyxxmore.aspx?catgorynum1=011&catgorynum2=009&xiaqu=&type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_jiaotong_zhaobiao_gg",
     "http://ggzy.liuzhou.gov.cn/gxlzzbw/showinfo/jyxxmore.aspx?catgorynum1=008&catgorynum2=001&xiaqu=&type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_jiaotong_zhongbiaohx_gg",
     "http://ggzy.liuzhou.gov.cn/gxlzzbw/showinfo/jyxxmore.aspx?catgorynum1=008&catgorynum2=002&xiaqu=&type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_jiaotong_zhongbiao_gg",
     "http://ggzy.liuzhou.gov.cn/gxlzzbw/showinfo/jyxxmore.aspx?catgorynum1=008&catgorynum2=009&xiaqu=&type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["zfcg_zhaobiao_gg",
     "http://ggzy.liuzhou.gov.cn/gxlzzbw/showinfo/jyxxmore.aspx?catgorynum1=004&catgorynum2=006&xiaqu=&type=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://ggzy.liuzhou.gov.cn/gxlzzbw/showinfo/jyxxmore.aspx?catgorynum1=004&catgorynum2=008&xiaqu=&type=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://ggzy.liuzhou.gov.cn/gxlzzbw/showinfo/jyxxmore.aspx?catgorynum1=004&catgorynum2=007&xiaqu=&type=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

def work(conp,**arg):
    est_meta(conp, data=data, diqu="广西省柳州市",**arg)
    est_html(conp, f=f3,**arg)


if __name__ == "__main__":

    conp=["postgres", "since2015", "192.168.3.171", "guangxi", "liuzhou"]
    work(conp)