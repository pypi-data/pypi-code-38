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

_name_="guigang"
def f1(driver,num):
    locator = (By.XPATH,'//ul[@class="wb-data-item"]/li/div/a')
    WebDriverWait(driver,20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//ul[@class="wb-data-item"]/li[1]/div/a').get_attribute("href")
    if WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="ewb-page pagemargin"]'))).text != '':
        cnum = driver.find_element_by_xpath('//li[@class="active"]/a').text
    else:cnum = 1
    if int(cnum) != int(num):
        url = re.sub(r'[about\d]+\.html', str(num)+'.html' if num != 1 else 'about' + '.html', driver.current_url)
        driver.get(url)
        locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]/div/a[not(contains(@href,"%s"))]'%val)
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    page = driver.page_source
    body = etree.HTML(page)
    data = []
    content_list = body.xpath('//ul[@class="wb-data-item"]/li')
    for content in content_list:

        name = content.xpath("./div/a")[0].xpath("string(.)")

        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = "http://ggggjy.gxgg.gov.cn:9005" + content.xpath("./div/a/@href")[0]
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"]=None
    return df


def f2(driver):

    if WebDriverWait(driver,20).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="ewb-page pagemargin"]'))).text !='':
        total_page = driver.find_element_by_xpath("//ul[@class='m-pagination-page']/li[last()]/a").text
    else:
        total_page = 1
    driver.quit()
    return int(total_page)

def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@class='tblInfo']|//div[@class='ewb-article']")
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
    if div == None:
        div = soup.find('div',class_='ewb-article')
    return div


data =[
    ##
    ["gcjs_fangjianshizheng_zhaobiao_guigang_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002001/002001001/002001001001/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_fangjianshizheng_biangeng_guigang_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002001/002001001/002001001002/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_fangjianshizheng_kongzhijia_guigang_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002001/002001001/002001001003/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_fangjianshizheng_zhongbiao_guigang_gg", # 有部分网页404
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002001/002001001/002001001004/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_guigang_gg", # 有部分网页404
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002001/002001003/002001003001/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_guigang_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002001/002001003/002001003002/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_kongzhijia_guigang_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002001/002001003/002001003003/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_guigang_gg", # 有部分网页404
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002001/002001003/002001003004/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_hetong_guigang_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002001/002001003/002001003005/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["gcjs_shuilijiaotong_zhaobiao_guigang_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002001/002001006/002001006001/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuilijiaotong_biangeng_guigang_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002001/002001002/002001002002/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuilijiaotong_kongzhijia_guigang_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002001/002001002/002001002003/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuilijiaotong_zhongbiaohx_guigang_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002001/002001006/002001006003/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_qita_zhaobiao_guigang_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002001/002001006/002001006001/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_qita_zhongbiao_guigang_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002001/002001006/002001006003/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ##桂平市
    ["gcjs_fangjianshizheng_zhaobiao_guiping_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002002/002002001/002002001001/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_fangjianshizheng_biangeng_guiping_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002002/002002001/002002001002/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_fangjianshizheng_kongzhijia_guiping_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002002/002002001/002002001003/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_fangjianshizheng_zhongbiao_guiping_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002002/002002001/002002001004/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_guiping_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002002/002002003/002002003001/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_guiping_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002002/002002003/002002003002/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_kongzhijia_guiping_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002002/002002003/002002003003/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_guiping_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002002/002002003/002002003004/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_hetong_guiping_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002002/002002003/002002003005/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_shuilijiaotong_zhaobiao_guiping_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002002/002002002/002002002001/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuilijiaotong_biangeng_guiping_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002002/002002002/002002002002/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuilijiaotong_kongzhijia_guiping_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002002/002002002/002002002003/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuilijiaotong_zhongbiaohx_guiping_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002002/002002002/002002002004/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_qita_zhaobiao_guiping_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002002/002002006/002002006001/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ##
    ["gcjs_fangjianshizheng_zhaobiao_pingnan_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002003/002003001/002003001001/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_fangjianshizheng_biangeng_pingnan_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002003/002003001/002003001002/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_fangjianshizheng_kongzhijia_pingnan_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002003/002003001/002003001003/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_fangjianshizheng_zhongbiao_pingnan_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002003/002003001/002003001004/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_pingnan_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002003/002003003/002003003001/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_pingnan_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002003/002003003/002003003002/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_hetong_pingnan_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002003/002003003/002003003005/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_pingnan_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002003/002003003/002003003004/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_shuilijiaotong_zhaobiao_pingnan_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002003/002003002/002003002001/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuilijiaotong_biangeng_pingnan_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002003/002003002/002003002002/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuilijiaotong_kongzhijia_pingnan_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002003/002003002/002003002003/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuilijiaotong_zhongbiaohx_pingnan_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002003/002003002/002003002004/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_qita_zhongbiaohx_pingnan_gg",
     "http://ggggjy.gxgg.gov.cn:9005/zbxx/002003/002003006/002003006003/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]

def work(conp,**arg):
    est_meta(conp, data=data, diqu="广西省贵港市",**arg)
    est_html(conp, f=f3,**arg)



if __name__ == "__main__":
    # conp=["postgres", "since2015", "192.168.3.171", "guangxi", "guigang"]

    # work(conp,num=4,total=10)
    url= "http://ggggjy.gxgg.gov.cn:9005/zbxx/002001/002001003/002001003001/about.html"
    driver = webdriver.Chrome()
    driver.get(url)
    for i in range(100,123): print(f1(driver, i))