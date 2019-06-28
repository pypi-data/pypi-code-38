import re
import time

from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong.util.etl import est_html, est_meta, add_info
import requests
from time import sleep

_name_ = "changzhou"


def f3(driver, url):
    driver.get(url)
    locator = (By.CLASS_NAME, "detail-info")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    sleep(0.5)
    before = len(driver.page_source)
    sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 5: break

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_='detail-info')
    return div


def f1(driver, num):
    locator = (By.XPATH, '//*[@id="showList"]/li[1]/a')
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
    val = driver.find_element_by_xpath('//div[@id="showList"]/li[1]/a').get_attribute("href")[-50:]

    cnum = int(driver.find_element_by_xpath('//span[@class="pg_maxpagenum"]').text.split('/')[0])
    if cnum != int(num):
        locator = (By.XPATH, '//input[@class="pg_num_input"]')
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
        driver.find_element_by_xpath('//input[@class="pg_num_input"]').clear()
        driver.find_element_by_xpath('//input[@class="pg_num_input"]').send_keys(num)
        driver.find_element_by_class_name("pg_gobtn").click()

        locator = (By.XPATH, "//div[@id='showList']/li[1]/a[not(contains(@href,'%s'))]" % val)

        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@id='showList']/li")
    js_temp = """
    function redirectpage(infoid,categorynum){
        var data={};
        var result;
        data.infoid=infoid;
        data.siteGuid=siteInfo.siteGuid;
        data.categorynum=categorynum;
            $.ajax({
                url: siteInfo.projectName + "/frontPageRedirctAction.action?cmd=pageRedirect",
                type: "post",
                data: data,
                dataType: "json",
                async: false,
                cache: false,
            })
            .success(function (msg) {
            result = msg.custom;
            })
            return  result;
      
	};"""

    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        js=js_temp + "\n" + content.xpath("./a/@href")[0]
        # js=js.replace("redirectpage","redirect_page")
        js = js.replace('javascript:','return ')
        try:
            url = 'http://58.216.50.99:8089'+driver.execute_script(js)
        except:url ='网站链接失效，无法获取。'
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//span[@class="pg_maxpagenum"]')
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
    total_page = int(driver.find_element_by_class_name('pg_maxpagenum').text.split('/')[1])
    driver.quit()
    return total_page


data = [

    ["gcjs_zhaobiao_gg",
     "http://58.216.50.99:8089/jyzx/about_jyxx.html?cate=001001001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://58.216.50.99:8089/jyzx/about_jyxx.html?cate=001001005",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://58.216.50.99:8089/jyzx/about_jyxx.html?cate=001001006",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuili_zhaobiao_gg",
     "http://58.216.50.99:8089/jyzx/about_jyxx.html?cate=001003001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"gctype":"水利"}), f2],
    ["gcjs_shuili_zhongbiao_gg",
     "http://58.216.50.99:8089/jyzx/about_jyxx.html?cate=001003003",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"gctype":"水利"}), f2],
    ["zfcg_zhaobiao_gg",
     "http://58.216.50.99:8089/jyzx/about_jyxx.html?cate=001004002",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://58.216.50.99:8089/jyzx/about_jyxx.html?cate=001004006",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://58.216.50.99:8089/jyzx/about_jyxx.html?cate=001004003",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="江苏省常州市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "jiangsu", "changzhou"],headless=False,num=2)
    # driver = webdriver.Chrome()
    # driver.get('http://58.216.50.99:8089/jyzx/about_jyxx.html?cate=001004002')
    # for i in range(1,200):f1(driver,i)
    # driver.quit()
