import os
import pandas as pd
import re
import requests
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zlshenpi.util.etl import add_info, est_meta, est_html, est_tbs, add_info, est_meta_large
import sys
import time
import json
from zlshenpi.util.fake_useragent import UserAgent

ua = UserAgent()
_name_ = "hunansheng"

proxy = {}


def get_ip():
    global proxy
    try:
        url = """http://ip.11jsq.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=0&fa=0&fetch_key=&qty=1&time=1&pro=&city=&port=1&format=txt&ss=1&css=&dt=1&specialTxt=3&specialJson="""
        r = requests.get(url)
        time.sleep(1)
        ip = r.text
        proxy = {'http': ip}
    except:
        proxy = {}
    return proxy


def requests_hb(post_url):
    global proxy
    if proxy == {}:get_ip()
    try:
        response = requests.get(post_url, headers={"User-Agent": ua.random, "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"}, timeout=40, proxies=proxy)
    except:
        proxy = get_ip()
        response = requests.get(post_url, headers={"User-Agent": ua.random, "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"}, timeout=40, proxies=proxy)
    return response


def f1(driver, num):
    locator = (By.XPATH, "//ul[@id='show_page']/li[1]/div[1]/a")
    val = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).get_attribute("href")[-30:]
    # print(val)
    locator = (By.XPATH, "//span[@class='current']")
    cnum = int(WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('paged'))
    if num != int(cnum):
        js = """
        function goto(page){
             var url = "/portal/zcfg/busiotherpublicinfo!createPage.action";
             initEvent(url ,page , '',"demo","show_page");
        };goto(%s)""" % num

        driver.execute_script(js)

        locator = (By.XPATH, """//ul[@id='show_page']/li[1]/div[1]/a[not(contains(@href, "%s"))]""" % val)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    body = etree.HTML(page)
    contents = body.xpath("//ul[@id='show_page']/li")
    data = []
    for content in contents:
        name = content.xpath('./div[1]/a/@title')[0].strip()
        bumen = content.xpath('./div[1]/a/span/text()')[0].strip().strip('[').strip(']')

        xm_code = content.xpath('./div[2]/a/span/text()')[0].strip()

        piwenhao = content.xpath('./div[3]/a/span/text()')[0].strip()

        href = 'http://www.hntzxm.gov.cn' + content.xpath('./div[1]/a/@href')[0].strip()
        ggstart_time = content.xpath('./div[4]/a/span/text()')[0].strip()
        info_tmp = {"piwenhao": piwenhao, 'bumen': bumen, "xm_code": xm_code}
        if 'javascript:void(0);' in href:
            href = "None"
            info_tmp.update({'hreftype':'不可抓网页'})
        info = json.dumps(info_tmp, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="Page badoo"]/a[contains(string(),"尾页")]')
    total_page = int(WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).get_attribute('paged'))
    driver.quit()
    return total_page


def f3(driver, url):
    file_p = os.path.join(os.path.dirname(__file__), 'default_path.txt')
    with open(file_p, 'r') as f: default_path = re.findall('\"([^"]+)\"', f.read())[0]
    o_url = 'http://www.hntzxm.gov.cn/portal/zcfg/busiotherpublicinfo!selectPublicInfo.action?tn=3'
    driver.get(o_url)
    if not os.path.exists('%s'%default_path):os.mkdir('%s'%default_path)
    if not os.path.exists('%s%s_files' % (default_path,_name_)): os.mkdir('%s%s_files' %(default_path,_name_))

    id = url.split('=')[-1]
    response = requests_hb(url)
    # print(response.headers['Content-Disposition'].encode('ISO-8859-1').decode('gbk'))
    try:
        filename = re.findall('\"([^"]+)\"', response.headers['Content-Disposition'].encode('ISO-8859-1').decode('gb2312'))[0]
    except:
        filename = re.findall('\"([^"]+)\"', response.headers['Content-Disposition'].encode('ISO-8859-1').decode('gbk'))[0]

    if not os.path.exists('%s%s_files/%s_%s' % (default_path,_name_, id, filename)):
        with open('%s%s_files/%s_%s' % (default_path,_name_, id, filename), 'wb') as f:
            f.write(response.content)
    div = '文件保存为 %s%s_files/%s_%s' % (default_path, _name_,id, filename)
    return div


data = [
    ["xm_shenpi_gg",
     "http://www.hntzxm.gov.cn/portal/zcfg/busiotherpublicinfo!selectPublicInfo.action?tn=3",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="湖南省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    # work(conp=["postgres", "since2015", "192.168.3.171", "zlshenpi", "hunansheng"])
    driver = webdriver.Chrome()
    # for d in data:
    #     driver.get(d[1])
    #         # print(d[1])
    #     for i in range(13560,13600):
    #         print(f1(driver, i))

    # print(f2(driver))

    print(f3(driver, 'http://www.hntzxm.gov.cn/portal/zcfg/attach.action?id=297edff8542461480154b73e55936c35'))
