import time

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from zhulong2.util.etl import est_tbs, est_meta, est_html, est_gg


# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hengyang.gov.cn/jyxx/jsgc/zbgg_64796/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='hubei_jingmen'


def f1(driver,num):
    locator = (By.XPATH, '//div[@class="box"]/div[1]//li[1]/span[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url = driver.current_url

    cnum = int(re.findall("page=(\d+)", url)[0])

    if num != cnum:
        s = "page=%d" % (num)

        url_ = re.sub("page=(\d+)", s, url)

        val = driver.find_element_by_xpath('//div[@class="box"]/div[1]//li[1]/span[2]/a').get_attribute('href')[-15:]
        driver.get(url_)

        locator = (By.XPATH, '//div[@class="box"]/div[1]//li[1]/span[2]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    ht = driver.page_source
    soup = BeautifulSoup(ht, 'html.parser')
    div = soup.find('div', class_="box").find('div', class_="list")
    uls = div.find_all('li')

    data = []
    for li in uls:
        name = li.find('span', class_="li_name").a['title']
        href = li.find("span", class_="li_name").a['href']

        if 'http' in href:
            href = href
        else:
            href = 'http://www.jmzfcg.com/' + href
        ggstart_time = li.find('span', class_="date").get_text().strip(']').strip('[')

        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="box"]/div[1]//li[1]/span[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//div[@class="page"]').text

    total = re.findall('当前.+?/(.+?)页', total)[0].strip()

    total=int(total)

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="con"][string-length()>10]')

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
    div = soup.find('div',class_="con")
    return div




data=[
    ##包含招标,需求
    ["zfcg_zhaobiao_gg","http://zfcgzx.jingmen.gov.cn/article.php?act=list&typeid=3&page=1",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_gqita_da_bian_gg","http://zfcgzx.jingmen.gov.cn/article.php?act=list&typeid=4&page=1",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_zhongbiao_1_gg","http://zfcgzx.jingmen.gov.cn/article.php?act=list&typeid=5&page=1",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_zhongbiao_2_gg","http://zfcgzx.jingmen.gov.cn/article.php?act=list&typeid=6&page=1",["name","ggstart_time","href",'info'],f1,f2],

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="湖北省荆门市",**args)
    est_html(conp,f=f3,**args)


##网站变更 http://zfcgzx.jingmen.gov.cn
##修改时间 2019-5-22


if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","lch","hubei_jingmen"]

    work(conp=conp,headless=False,num=1)