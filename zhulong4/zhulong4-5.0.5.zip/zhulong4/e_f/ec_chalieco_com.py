import math
import re
import json
import requests
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong4.util.etl import est_html, est_meta
import time

_name_ = 'ec_chalieco_com'


def f1(driver, num):
    locator = (By.XPATH,'//table[@class="datatlb"]/tbody/tr')
    WebDriverWait(driver,20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//table[@class="datatlb"]/tbody/tr[2]/td/a').text
    cnum = driver.find_element_by_xpath("//input[@id='input_page']").get_attribute("value")
    if int(cnum) != int(num):
        driver.execute_script("javascript:queryData(%s)"%num)

        locator = (By.XPATH, '//table[@class="datatlb"]/tbody/tr[2]/td/a[not(contains(text(),"%s"))]'%val)
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    page = driver.page_source
    body = etree.HTML(page)
    data = []
    content_list = body.xpath('//table[@class="datatlb"]/tbody/tr')[1:]
    for content in content_list:
        name = content.xpath("./td/a/text()")[0].strip()
        ggstart_time = content.xpath("./td[2]/text()")[0].strip()
        url_list = content.xpath("./td/a/@onclick | ./td/a/@href")
        # print(url_list)
        if url_list[0] == '#':
            url_temp = re.findall('\'([^\']+)\'', url_list[1])[0]
        else:
            url_temp = re.findall('\'([^\']+)\'', url_list[0])[0]
        if "当前信息供应商登录后才能查看！" in url_temp:
            # 需要登录才能查看
            url = "当前信息供应商登录后才能查看！"
        elif "showPxjgmessage" in ''.join(url_list):
            # 询价结果公示
            url = "http://ec.chalieco.com/b2b/web/two/indexinfoAction.do?actionType=showPxjgDetail&xxbh=" + url_temp
        elif "showCgxjMessage" in ''.join(url_list):
            # 询价公告
            url = "http://ec.chalieco.com/b2b/web/two/indexinfoAction.do?actionType=showCgxjDetail&xjbm=" + url_temp
        elif "showCqggMessage" in ''.join(url_list):
            # 澄清公告
            url = "http://ec.chalieco.com/b2b/web/two/indexinfoAction.do?actionType=showCgxjDetail&xjbm=" + url_temp
        elif "showZhongbggMessage" in ''.join(url_list):
            url = "http://ec.chalieco.com/b2b/web/two/indexinfoAction.do?actionType=showZhongbggDetail&xxbh=" + url_temp + '&inviteid=undefined'
        elif "showZbsMessage" in ''.join(url_list):
            url = "http://ec.chalieco.com/b2b/web/two/indexinfoAction.do?actionType=showZbsDetail&inviteid=" + url_temp

        temp = [name, ggstart_time, url]

        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"]=None
    return df

def f2(driver):
    WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,'//td[@width="150"]')))
    total_page = re.findall(r'\/ (\d+)',driver.find_element_by_xpath('//td[@width="150"]').text)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="main-news"]')
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
    div = soup.find('div',class_="main-news")

    return div


data = [
    ["qy_zhaobiao_1_gg",
     "http://ec.chalieco.com/b2b/web/two/indexinfoAction.do?actionType=showMoreCgxx&xxposition=cgxx",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_zhaobiao_gg",
     "http://ec.chalieco.com/b2b/web/two/indexinfoAction.do?actionType=showMoreZbs&xxposition=zbgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_biangeng_gg",
     "http://ec.chalieco.com/b2b/web/two/indexinfoAction.do?actionType=showMoreClarifypub&xxposition=cqgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_zhongbiao_gg",
     "http://ec.chalieco.com/b2b/web/two/indexinfoAction.do?actionType=showMorePub&xxposition=zhongbgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="中国铝业集团有限公司", **args)
    est_html(conp, f=f3, **args)

def main():
    conp = ["postgres", "since2015", "192.168.3.171", "anbang_qiye", "ec_chalieco_com"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://ec.chalieco.com/b2b/web/two/indexinfoAction.do?actionType=showMoreCgxx&xxposition=cgxx")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 8)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # driver.get("http://ec.chalieco.com/b2b/web/two/indexinfoAction.do?actionType=showMoreClarifypub&xxposition=cqgg")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 8)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://ec.chalieco.com/b2b/web/two/indexinfoAction.do?actionType=showCgxjDetail&xjbm=1BAD2A4E611CAD79D968C5D5C1ABAB8C'))
    # print(1111111)
    # print(f3(driver, 'http://ec.chalieco.com/b2b/web/two/indexinfoAction.do?actionType=showCgxjDetail&xjbm=1BAD2A4E611CAD7925B49FC6150E6CFC'))
    # print(2222222222222)
    # print(f3(driver, 'http://ec.chalieco.com/b2b/web/two/indexinfoAction.do?actionType=showCqggDetail&xxbh=D01E234D6749D418F46C85D1CA17E008'))
    # print(1111111)
    # print(f3(driver, 'http://ec.chalieco.com/b2b/web/two/indexinfoAction.do?actionType=showPxjgDetail&xxbh=470077CB7E6492C80298C3AB8699F1B6'))
    # driver.close()
if __name__ == "__main__":
    main()