import pandas as pd
import re

import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write, db_command, db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html
from zhulong.util.fake_useragent import UserAgent

from zhulong.util.etl import add_info

_name_ = 'qingyang'


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="trad-sear-con"]//li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//li[@class="active pageno"]/a')
    cnum = int(WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text)

    if num != cnum:
        page_count = len(driver.page_source)
        val = driver.find_element_by_xpath('//div[@class="trad-sear-con"]//li[1]/a').get_attribute('onclick')[-30:-5]

        driver.execute_script("page(%s,20,'');" % num)

        locator = (By.XPATH, "//div[@class='trad-sear-con']//li[1]/a[not(contains(@onclick,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        WebDriverWait(driver, 10).until(lambda driver: len(driver.page_source) != page_count)
    page = driver.page_source

    soup = BeautifulSoup(page, "html.parser")

    div = soup.find("div", class_="trad-sear-con")

    dls = div.find_all("li")

    data = []

    for dl in dls:
        name = dl.find("a")['title']
        href = dl.find("a")['onclick']
        ggstart_time = dl.find("span").text.strip()
        href ='http://www.qyggfw.cn'+ re.findall("href='(.+)'",href)[0]

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df



def f2(driver):
    locator=(By.XPATH,'//div[@class="trad-sear-con"]//li[1]/a')
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//li[@class="active pageno"]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:

        total=driver.find_element_by_xpath('//div[@class="tradpage"]//li[@class="pageno"][last()]/a').text
        total=int(total)
    except:
        total=1

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="mod-arti-area "][string-length()>100]')

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

    div = soup.find('div', class_='mod-arti-area ')
    if div == None:
        raise  ValueError

    return div


data=[
["gcjs_zhaobiao_gg",'http://www.qyggfw.cn/w/bid/tenderAnnQuaInqueryAnn/morePageList?filterparam={%22assortment%22:%220%22,%22areaCode%22:%22621000%22,%22workNotice%22:{%22noticeNature%22:%221%22,%22bulletinType%22:%221%22}}',["name","ggstart_time","href","info"],f1,f2],
["gcjs_zgys_gg",'http://www.qyggfw.cn/w/bid/tenderAnnQuaInqueryAnn/morePageList?filterparam={"assortment":"1","areaCode":"621000","workNotice":{"noticeNature":"1","bulletinType":"2"}}',["name","ggstart_time","href","info"],f1,f2],
["gcjs_biangeng_gg",'http://www.qyggfw.cn/w/bid/tenderAnnQuaInqueryAnn/morePageList?filterparam={%22assortment%22:%222%22,%22areaCode%22:%22621000%22,%22workNotice%22:{%22noticeNature%22:%222%22,%22bulletinType%22:%22%22}}',["name","ggstart_time","href","info"],f1,f2],
["gcjs_zgysjg_gg",'http://www.qyggfw.cn/w/bid/qualiInqueryResult/morePageList?filterparam={"assortment":"3","areaCode":"621000","workNotice":{"noticeNature":"1","bulletinType":"1"}}',["name","ggstart_time","href","info"],f1,f2],
["gcjs_zhongbiao_gg",'http://www.qyggfw.cn/w/bid/winResultAnno/morePageList?filterparam={"assortment":"4","areaCode":"621000","workNotice":{"noticeNature":"1","bulletinType":"3"}}',["name","ggstart_time","href","info"],f1,f2],
#

["zfcg_zhaobiao_gg",'http://www.qyggfw.cn/w/bid/purchaseQualiInqueryAnn/morePageList?filterparam=%7B%22assortment%22%3A%220%22%2C%22areaCode%22%3A%22621000%22%2C%22workNotice%22%3A%7B%22noticeNature%22%3A%221%22%2C%22bulletinType%22%3A%221%22%7D%7D',["name","ggstart_time","href","info"],f1,f2],
["zfcg_biangeng_gg",'http://www.qyggfw.cn/w/bid/correctionItem/morePageList?filterparam=%7B%22assortment%22%3A%221%22%2C%22areaCode%22%3A%22621000%22%2C%22workNotice%22%3A%7B%22noticeNature%22%3A%221%22%2C%22bulletinType%22%3A%221%22%7D%7D',["name","ggstart_time","href","info"],f1,f2],
["zfcg_zhongbiao_gg",'http://www.qyggfw.cn/w/bid/correctionItem/morePageList?filterparam={%22assortment%22:%222%22,%22areaCode%22:%22621000%22,%22workNotice%22:{%22noticeNature%22:%221%22,%22bulletinType%22:%221%22}}',["name","ggstart_time","href","info"],f1,f2],


    ]

def work(conp,**args):
    est_meta(conp,data=data,diqu="甘肃省庆阳市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    work(conp=["postgres","since2015",'192.168.3.171',"gansu","qingyang"],headless=True,num=1,total=2)
    # driver=webdriver.Chrome()
    # f3(driver,'http://www.qyggfw.cn/w/bid/purchaseQualiInqueryAnn/37304/details.html')