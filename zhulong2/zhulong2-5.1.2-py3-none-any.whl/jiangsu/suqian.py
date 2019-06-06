import pandas as pd
import re
from lxml import etree
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

from zhulong2.util.etl import est_meta, est_html, add_info

_name_ = 'jiangsu_suqian'


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               "//div[@class='fdiv']//div[@class='article'] | //div[@class='fdiv']//  div[@class='sub_content'] | //div[@class='sub_content']")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))

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

    div1 = soup.find('div', attrs={'id': re.compile('d\d+'), 'class': 'fdiv'})
    # print(div1)
    try:
        div1 = div1.find_all('div', class_='sub_content')
    except:
        if div1 == None:
            div1 = soup.find('div', class_='sub_content')
        else:
            raise Exception
    return div1


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='sub_content']/dl/dt/a")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//div[@class="sub_content"]/dl[1]/dt/a').get_attribute("href")[-40:]
    if "zfcgCggg" in driver.current_url:
        cnum = driver.find_element_by_xpath("//span[@id='pageNo']").text
    else:
        cnum = re.findall('(\d+)/', driver.find_element_by_xpath("//div[@class='digg']/div").text)[0]
    # print('val', val, 'cnum', cnum,"num",num)
    if int(cnum) != int(num):
        if "zfcgCggg" in driver.current_url:
            driver.execute_script("pageChange(%s)" % num)
        else:
            url = driver.current_url
            url = re.sub(r'index[\d_]*', 'index_' + str(num), url, count=1)
            driver.get(url)
            # print(url)
        locator = (By.XPATH, '//div[@class="sub_content"]/dl[1]/dt/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
    data = []
    url_part = driver.current_url
    url_part = url_part.rsplit('/', maxsplit=1)[0]
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@class='sub_content']/dl")
    for content in content_list:
        name = content.xpath("./dt/a/text()")[0].strip()
        ggstart_time = content.xpath('./dd/text()')[0].strip()
        if "http://" not in content.xpath("./dt/a/@href")[0].strip():
            if "zfcgCggg" in driver.current_url:
                href = url_part + '/' + content.xpath("./dt/a/@href")[0].strip()
            else:
                href = 'http://zfcg.suqian.gov.cn/' + content.xpath("./dt/a/@href")[0].split('/', maxsplit=3)[-1]
        else:
            if "zfcgCggg" in driver.current_url:
                href = content.xpath("./dt/a/@href")[0].strip()
            else:
                href = content.xpath("./dt/a/@href")[0].strip().split('/', maxsplit=3)[-1]
        temp = [name, ggstart_time, href]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    if "zfcgCggg" in driver.current_url:
        locator = (By.XPATH, "//span[@id='totalPage']")
        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
        total_page = driver.find_element_by_xpath("//span[@id='totalPage']").text
    else:
        locator = (By.XPATH, "//div[@class='digg']")
        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
        total_page = re.findall('/(\d+)', driver.find_element_by_xpath("//div[@class='digg']/div").text)[0]
    driver.quit()
    return int(total_page)


data = [
    #
    ["zfcg_zhaobiao_gongkai_gg", "http://zfcg.suqian.gov.cn/zfcgCggg/ggList.html?gglb=gkzb",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'公开'}), f2],
    ["zfcg_zhaobiao_tanpan_gg", "http://zfcg.suqian.gov.cn/zfcgCggg/ggList.html?gglb=jztp",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'谈判'}), f2],
    ["zfcg_zhaobiao_cuoshang_gg", "http://zfcg.suqian.gov.cn/zfcgCggg/ggList.html?gglb=jzcs",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'磋商'}), f2],
    ["zfcg_zhaobiao_danyilaiyuan_gg", "http://zfcg.suqian.gov.cn/zfcgCggg/ggList.html?gglb=dyly",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'单一来源'}), f2],
    ["zfcg_zhaobiao_xunjia_gg", "http://zfcg.suqian.gov.cn/zfcgCggg/ggList.html?gglb=xjgg",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'询价'}), f2],
    ["zfcg_zhongbiao_gg", "http://zfcg.suqian.gov.cn/zfcgCggg/ggList.html?gglb=zbgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_chengjiao_gg", "http://zfcg.suqian.gov.cn/zfcgCggg/ggList.html?gglb=cjgg",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'成交'}), f2],
    ["zfcg_liubiao_gg", "http://zfcg.suqian.gov.cn/zfcgCggg/ggList.html?gglb=zzgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg", "http://zfcg.suqian.gov.cn/zfcgCggg/ggList.html?gglb=gzgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_gqita_gg", "http://zfcg.suqian.gov.cn/zfcgCggg/ggList.html?gglb=qtgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_yucai_old_gg", "http://zfcg.suqian.gov.cn/cgxxgg/cgygg/index.html", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'tag': '旧'}), f2],
    ["zfcg_zhaobiao_old_gg", "http://zfcg.suqian.gov.cn/cgxxgg/cggg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'tag': '旧'}), f2],
    ["zfcg_zhaobiao_danyilaiyuan_old_gg", "http://zfcg.suqian.gov.cn/rzgs/dylygs/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'tag': '旧','method':'单一来源'}), f2],
    ["zfcg_biangeng_old_gg", "http://zfcg.suqian.gov.cn/cgxxgg/bggg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'tag': '旧'}), f2],
    ["zfcg_zhongbiao_1_old_gg", "http://zfcg.suqian.gov.cn/cgxxgg/jggg/index.html", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {'tag': '旧','tag2':'结果'}), f2],
    ["zfcg_yanshou_old_gg", "http://zfcg.suqian.gov.cn/cgxxgg/ysgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'tag': '旧'}), f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="江苏省宿迁市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "jiangsu_suqian"])
