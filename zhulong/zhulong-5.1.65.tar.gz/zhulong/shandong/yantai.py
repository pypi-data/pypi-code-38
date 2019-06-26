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
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs
from collections import OrderedDict


_name_='yantai'


def f1(driver,num):
    locator = (By.XPATH, "//ul[@class='article-list2']/li[1]/div/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # 获取当前页的url
    url = driver.current_url
    locator = (By.XPATH, '(//ul[@class="pages-list"]/li)[1]')
    page_all = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall('(\d+)/', page_all)[0]
    if num != int(cnum):
        if num == 1:
            url = re.sub("queryContent_[0-9]*-", "queryContent_1-", url)
        else:
            s = "queryContent_%d-" % (num) if num > 1 else "queryContent_1-"
            url = re.sub("queryContent_[0-9]*-", s, url)
        val = driver.find_element_by_xpath('//ul[@class="article-list2"]/li[1]/div/a').get_attribute('href')[-30:]
        driver.get(url)
        locator = (By.XPATH, "//ul[@class='article-list2']/li[1]/div/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    ul = soup.find("ul", class_="article-list2")
    trs = ul.find_all("li")
    data = []
    for li in trs:
        try:
            info_number = li.find("span", class_="blue-w").text
            diqu = re.findall(r"\[(.*)\]", info_number)[0]
        except:
            diqu = "-"
        a = li.find("a")
        title = a["title"]
        link = a["href"]
        try:
            date = li.find("div", class_="list-times").text
        except:
            date = li.find("p", class_="bmZhong").text
        if '至' in date:
            date1 = re.findall(r'(\d+-\d+-\d+)', date)[0]
            date2 = re.findall(r'(\d+-\d+-\d+)', date)[1]
            info = json.dumps({'diqu':diqu, 'end_time':date2}, ensure_ascii=False)
            tmp = [title.strip(), date1.strip(), link.strip(), info]
            data.append(tmp)
        else:
            info = json.dumps({'diqu':diqu}, ensure_ascii=False)
            tmp = [title.strip(), date.strip(), link.strip(), info]
            data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, "//ul[@class='article-list2']/li[1]/div/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '(//ul[@class="pages-list"]/li)[1]')
    page_all = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    page = re.findall('/(\d+)', page_all)[0]

    driver.quit()
    return int(page)


def f3(driver,url):
    driver.get(url)
    locator=(By.XPATH,"//div[@class='content-warp'][string-length()>30]")
    WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))
    try:
        driver.switch_to.frame(0)
        page=driver.page_source
        before=len(driver.page_source)
        time.sleep(0.1)
        after=len(driver.page_source)
        i=0
        while before!=after:
            before=len(driver.page_source)
            time.sleep(0.3)
            after=len(driver.page_source)
            i+=1
            if i>10:break
        page=driver.page_source
        soup=BeautifulSoup(page,'html.parser')
        div=soup.find('body')
        return div
    except:
        pass
    before=len(driver.page_source)
    time.sleep(0.1)
    after=len(driver.page_source)
    i=0
    while before!=after:
        before=len(driver.page_source)
        time.sleep(0.2)
        after=len(driver.page_source)
        i+=1
        if i>5:break
    page=driver.page_source
    soup=BeautifulSoup(page,'html.parser')
    div=soup.find('div',class_='content-warp')
    return div

data = [
        ["gcjs_zhaobiao_gg",
            "http://www.ytggzyjy.gov.cn:9082/queryContent_1-jyxx.jspx?title=&inDates=&ext=&origin=&channelId=264",
         ["name", "ggstart_time", "href", "info"], f1, f2],

        ["gcjs_zhaobiao_yaoqing_gg",
         "http://www.ytggzyjy.gov.cn:9082/queryContent_1-jyxx.jspx?title=&inDates=&ext=&origin=&channelId=265",
         ["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'邀请招标'}), f2],

        ["gcjs_zgys_gg",
         "http://www.ytggzyjy.gov.cn:9082/queryContent_1-jyxx.jspx?title=&inDates=&ext=&origin=&channelId=266",
         ["name", "ggstart_time", "href", "info"], f1, f2],

        ["gcjs_biangeng_gg",
         "http://www.ytggzyjy.gov.cn:9082/queryContent_1-jyxx.jspx?title=&inDates=&ext=&origin=&channelId=272",
         ["name", "ggstart_time", "href", "info"], f1, f2],

        ["gcjs_dayi_gg",
         "http://www.ytggzyjy.gov.cn:9082/queryContent_1-jyxx.jspx?title=&inDates=&ext=&origin=&channelId=267",
         ["name", "ggstart_time", "href", "info"], f1, f2],

        ["gcjs_zgysjg_gg",
         "http://www.ytggzyjy.gov.cn:9082/queryContent_1-jyxx.jspx?title=&inDates=&ext=&origin=&channelId=270",
         ["name", "ggstart_time", "href", "info"], f1, f2],

        ["gcjs_zhongbiaohx_gg",
         "http://www.ytggzyjy.gov.cn:9082/queryContent_1-jyxx.jspx?title=&inDates=&ext=&origin=&channelId=269",
         ["name", "ggstart_time", "href", "info"], f1, f2],

        ["gcjs_zhongbiao_gg",
         "http://www.ytggzyjy.gov.cn:9082/queryContent_1-jyxx.jspx?title=&inDates=&ext=&origin=&channelId=271",
         ["name", "ggstart_time", "href", "info"], f1, f2],

        ["gcjs_hetong_gg",
        "http://www.ytggzyjy.gov.cn:9082/queryContent_1-jyxx.jspx?title=&inDates=&ext=&origin=&channelId=349",
         ["name", "ggstart_time", "href", "info"], f1, f2],

        ["zfcg_yucai_gg",
         "http://www.ytggzyjy.gov.cn:9082/queryContent_1-jyxxZc.jspx?title=&inDates=&ext=&origin=&channelId=344",
         ["name", "ggstart_time", "href", "info"], f1, f2],

        ["zfcg_zhaobiao_gg",
         "http://www.ytggzyjy.gov.cn:9082/queryContent_1-jyxxZc.jspx?title=&inDates=&ext=&origin=&channelId=274",
         ["name", "ggstart_time", "href", "info"], f1, f2],

        ["zfcg_biangeng_gg",
         "http://www.ytggzyjy.gov.cn:9082/queryContent_1-jyxxZc.jspx?title=&inDates=&ext=&origin=&channelId=276",
         ["name", "ggstart_time", "href", "info"], f1, f2],

        ["zfcg_gqita_zhong_liu_gg",
         "http://www.ytggzyjy.gov.cn:9082/queryContent_1-jyxxZc.jspx?title=&inDates=&ext=&origin=&channelId=275",
         ["name", "ggstart_time", "href", "info"], f1, f2],

        ["zfcg_hetong_gg",
         "http://www.ytggzyjy.gov.cn:9082/queryContent_1-jyxxZc.jspx?title=&inDates=&ext=&origin=&channelId=278",
         ["name", "ggstart_time", "href", "info"], f1, f2],

        ["zfcg_yanshou_gg",
         "http://www.ytggzyjy.gov.cn:9082/queryContent_1-jyxxZc.jspx?title=&inDates=&ext=&origin=&channelId=277",
         ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp,**args):
    est_meta(conp,data=data,diqu="山东省烟台市")
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shandong","yantai"],pageloadtimeout=60,pageLoadStrategy="none")
