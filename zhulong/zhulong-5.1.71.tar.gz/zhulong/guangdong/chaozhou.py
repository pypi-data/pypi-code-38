import json

import pandas as pd
import re
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
from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, add_info, est_gg

# driver=webdriver.Chrome()
# url="http://www.bygzjy.cn/f/trade/annogoods/list?selectedProjectType=3"
# driver.get(url)

_name_ = 'chaozhou'


def f1(driver, num):
    locator = (By.XPATH, '//ul[@id="rows"]/li[1]//table[@align="left"]//input')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url=driver.current_url
    cnum=int(re.findall('pageNo=(\d+)',url)[0])

    if cnum != num:
        val = driver.find_element_by_xpath(
            '//ul[@id="rows"]/li[1]//table[@align="left"]//input').get_attribute('onclick')

        url=re.sub('pageNo=\d+','pageNo=%s'%num,url)
        driver.get(url)
        locator = (
            By.XPATH, '//ul[@id="rows"]/li[1]//table[@align="left"]//input[not(contains(@onclick,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("ul", id="rows")
    dls = div.find_all("li",class_='cells')
    data = []
    for dl in dls:
        box=dl.find('div',class_='box')
        lis=box.find_all('li')

        name=lis[0].find('h4').get_text()
        procode=lis[1].find_all('tr')[0].find_all('td')[1].get_text()
        ggstart_time=lis[1].find_all('tr')[1].find_all('td')[1].get_text()
        ggend_time=lis[1].find_all('tr')[2].find_all('td')[1].get_text()
        kaibiao_time=lis[1].find_all('tr')[3].find_all('td')[1].get_text()

        kongzhijia=lis[2].find_all('tr')[0].find_all('td')[1].get_text()
        zisheng=lis[2].find_all('tr')[1].find_all('td')[1].get_text()
        ggtype=lis[2].find_all('tr')[2].find_all('td')[1].get_text()

        zbdw=lis[3].find_all('tr')[0].find_all('td')[1].get_text()
        dljg=lis[3].find_all('tr')[1].find_all('td')[1].get_text()

        href=lis[3].find('input')['onclick']


        id_=re.findall('id:(.+?),',href)[0]
        clsid=re.findall('clsid:(.+?)}',href)[0].strip("'")


        if 'http' in href:
            href = href
        else:
            href = 'https://www.czggzy.com:8088/info.u.jsp?id={id_}&clsid={clid}'.format(id_=id_,clid=clsid)

        info={'procode':procode,"ggeng_time":ggend_time,"kaibiao_time":kaibiao_time,"kongzhijia":kongzhijia,"zisheng":zisheng,'ggtype':ggtype,"zbdw":zbdw,'dljg':dljg}

        info=json.dumps(info,ensure_ascii=False)

        tmp = [name, ggstart_time, href, info]

        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df


def f4(driver, num):
    locator = (By.XPATH, '//ul[@id="rows"]/table[1]//h3[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url=driver.current_url
    cnum=int(re.findall('pageNo=(\d+)',url)[0])

    if cnum != num:
        page_count=len(driver.page_source)
        val = driver.find_element_by_xpath(
            '//ul[@id="rows"]/table[1]').get_attribute('onclick')

        url=re.sub('pageNo=\d+','pageNo=%s'%num,url)
        driver.get(url)
        locator = (
            By.XPATH, '//ul[@id="rows"]/table[1][not(contains(@onclick,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        WebDriverWait(driver, 10).until(lambda driver:len(driver.page_source) != page_count)

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("ul", id="rows")
    dls = div.find_all("table",recursive=False)
    data = []
    for dl in dls:
        box=dl.find('div',class_='box2')
        lis=box.find_all('li')

        procode = lis[0].find_all('h3')[0].get_text().strip('项目编号：')
        name = lis[0].find_all('h3')[1].get_text().strip('项目名称：')
        ggtype = lis[0].find_all('h3')[2].get_text().strip('采购方式：')

        ggstart_time=lis[1].find_all('tr')[0].find_all('td')[1].get_text()
        ggend_time=lis[1].find_all('tr')[1].find_all('td')[1].get_text()
        kaibiao_time=lis[1].find_all('tr')[2].find_all('td')[1].get_text()


        href=dl['onclick']

        id_=re.findall('id:(.+?),',href)[0]
        clsid=re.findall('clsid:(.+?)}',href)[0].strip("'")


        if 'http' in href:
            href = href
        else:
            href = 'https://www.czggzy.com:8088/info.zu.jsp?id={id_}&clsid={clid}'.format(id_=id_,clid=clsid)

        info={'procode':procode,"ggeng_time":ggend_time,"kaibiao_time":kaibiao_time,'ggtype':ggtype}

        info=json.dumps(info,ensure_ascii=False)

        tmp = [name, ggstart_time, href, info]

        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df




def f2(driver):
    locator = (By.XPATH, '//ul[@id="rows"]/li[1]//table[@align="left"]//input')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//div[@class="bottom"]').text
    total = re.findall('条记录 (\d+?)页', total)[0]

    driver.quit()
    return int(total)

def f5(driver):
    locator = (By.XPATH, '//ul[@id="rows"]/table[1]//h3[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//div[@class="bottom"]').text
    total = re.findall('条记录 (\d+?)页', total)[0]

    driver.quit()
    return int(total)





def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@id="info"][string-length()>100]')
    WebDriverWait(
        driver, 10).until(
        EC.presence_of_all_elements_located(locator))

    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 5:
            break

    # f3 情况1
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', id='info')

    return div


data = [

    ["gcjs_gqita_gg",
     "https://www.czggzy.com:8088/indexj.jsp?pageNo=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_gg",
     "https://www.czggzy.com:8088/indexz.jsp?pageNo=1",
     ["name", "ggstart_time", "href", "info"], f4, f5],

]


## f3 为全流程 和 pdf


def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省潮州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(
        conp=[
            "postgres",
            "since2015",
            '192.168.3.171',
            "guangdong",
            "chaozhou_test"],
        )
