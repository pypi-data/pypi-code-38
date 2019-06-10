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

_name_="guilin"
def f1(driver,num):
    locator = (By.XPATH,'//li[@class="ewb-right-item clearfix"]/div/a')
    WebDriverWait(driver,20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//li[@class="ewb-right-item clearfix"]/div/a').text

    WebDriverWait(driver,20).until(EC.visibility_of_element_located(locator))
    cnum = re.findall("(\d+)/",driver.find_element_by_xpath("//td[@class='huifont']").text)[0]
    if int(cnum) != int(num):
        driver.execute_script("""window.location.href='./?Paging=%s'"""%num)

        locator = (By.XPATH, '//li[@class="ewb-right-item clearfix"]/div/a[not(contains(string(),"%s"))]'%val)
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    page = driver.page_source
    body = etree.HTML(page)
    data = []
    content_list = body.xpath('//li[@class="ewb-right-item clearfix"]')
    for content in content_list:
        name = content.xpath("./div/a")[0].xpath("string()")
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = "http://glggzy.org.cn" + content.xpath("./div/a/@href")[0]
        temp = [name, ggstart_time, url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df["info"]=None
    return df


def f2(driver):

    locator = (By.XPATH,"//td[@class='huifont']")
    WebDriverWait(driver,20).until(EC.visibility_of_element_located(locator))
    total_page = re.findall("/(\d+)",driver.find_element_by_xpath("//td[@class='huifont']").text)[0]
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
    return div


data =[

    ["gcjs_zhaobiao_gg",
     "http://glggzy.org.cn/gxglzbw/jyxx/001001/001001001/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_biangeng_gg",
     "http://glggzy.org.cn/gxglzbw/jyxx/001001/001001002/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_kongzhijia_gg",
     "http://glggzy.org.cn/gxglzbw/jyxx/001001/001001004/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://glggzy.org.cn/gxglzbw/jyxx/001001/001001006/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://glggzy.org.cn/gxglzbw/jyxx/001001/001001007/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_liubiao_gg",
     "http://glggzy.org.cn/gxglzbw/jyxx/001001/001001008/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_shuili_biangeng_gg",
     "http://glggzy.org.cn/gxglzbw/jyxx/001010/001010002/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuili_zhongbiaohx_gg",
     "http://glggzy.org.cn/gxglzbw/jyxx/001010/001010004/",
     ["name", "ggstart_time", "href", "info"], f1, f2],




    ["zfcg_zhaobiao_gg",
     "http://glggzy.org.cn/gxglzbw/jyxx/001004/001004001/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://glggzy.org.cn/gxglzbw/jyxx/001004/001004002/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiaohx_gg",
     "http://glggzy.org.cn/gxglzbw/jyxx/001004/001004004/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://glggzy.org.cn/gxglzbw/jyxx/001004/001004006/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_liubiao_gg",
     "http://glggzy.org.cn/gxglzbw/jyxx/001004/001004005/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

def work(conp,**arg):
    est_meta(conp, data=data, diqu="广西省桂林市",**arg)
    est_html(conp, f=f3,**arg)



if __name__ == "__main__":

    conp=["postgres", "since2015", "192.168.3.171", "guangxi", "guilin"]

    work(conp,num=3,total=10)