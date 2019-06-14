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

from zhulong.util.etl import est_tbs, est_meta, est_html, est_gg, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]

# url="http://ggzy.hengyang.gov.cn/jyxx/jsgc/zbgg_64796/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='gaoan'



def f1(driver,num):
    locator = (By.XPATH, '//*[@id="infolist"]/li[1]/div/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url = driver.current_url
    if "secondpageJyMk.html" in url:
        cnum = 1
    else:
        cnum = int(re.findall(r"/([0-9]{1,}).html", url)[0])
    if num != cnum:
        if num == 1:
            url = re.sub(r"[0-9]*.html", "secondpageJyMk.html", url)
        else:

            s = "/%d.html" % (num)
            url = url.rsplit('/', maxsplit=1)[0] + s
        val = driver.find_element_by_xpath('//*[@id="infolist"]/li[1]/div/a').get_attribute('href')[-30:-5]
        # print(val)
        driver.get(url)

        locator = (By.XPATH, "//*[@id='infolist']/li[1]/div/a[@href!='%s']"%val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find('ul', class_='wb-data-item')
    data = []

    urs = trs.find_all('li')
    for tr in urs:
        href = tr.a['href'].strip('.')
        if 'http' in href:
            href=href
        else:
            href = 'http://www.gaztbw.gov.cn' + href
        title = tr.a.get_text().strip()
        date_time = tr.span.get_text()
        tmp = [title, date_time,href]

        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):

    locator = (By.XPATH, '//*[@id="infolist"]/li[1]/div/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        try:
            page = driver.find_element_by_xpath('//*[@id="page"]/ul/li[10]/a').text
        except:
            page=driver.find_element_by_xpath("//ul[@class='m-pagination-page']/li[last()]").text
    except:
        page=1

    total=int(page)
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="ewb-detail-bd"] | //div[@class="article-info"]')

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
    div = soup.find('div',class_="article-info")
    if div == None:
        div=soup.find('div',class_="ewb-detail-bd")
    return div


data=[
    #
    ["gcjs_fangjianshizheng_zhaobiao_gg","http://www.gaztbw.gov.cn/jyxx/001001/001001001/secondpageJyMk.html",["name","ggstart_time","href",'info'],add_info(f1,{'gclx':"房建市政"}),f2],
    ["gcjs_fangjianshizheng_zhongbiaohx_gg","http://www.gaztbw.gov.cn/jyxx/001001/001001004/secondpageJyMk.html",["name","ggstart_time","href",'info'],add_info(f1,{'gclx':"房建市政"}),f2],
    ["gcjs_fangjianshizheng_gqita_da_bian_gg","http://www.gaztbw.gov.cn/jyxx/001001/001001002/secondpageJyMk.html",["name","ggstart_time","href",'info'],add_info(f1,{'gclx':"房建市政"}),f2],

    ["gcjs_jiaotong_zhaobiao_gg","http://www.gaztbw.gov.cn/jyxx/001002/001002001/secondpageJyMk.html",["name","ggstart_time","href",'info'],add_info(f1,{'gclx':"交通工程"}),f2],
    ["gcjs_jiaotong_zhongbiaohx_gg","http://www.gaztbw.gov.cn/jyxx/001002/001002003/secondpageJyMk.html",["name","ggstart_time","href",'info'],add_info(f1,{'gclx':"交通工程"}),f2],
    ["gcjs_jiaotong_gqita_da_bian_gg","http://www.gaztbw.gov.cn/jyxx/001002/001002002/secondpageJyMk.html",["name","ggstart_time","href",'info'],add_info(f1,{'gclx':"交通工程"}),f2],

    ["gcjs_shuili_zhaobiao_gg","http://www.gaztbw.gov.cn/jyxx/001003/001003001/secondpageJyMk.html",["name","ggstart_time","href",'info'],add_info(f1,{'gclx':"水利工程"}),f2],
    ["gcjs_shuili_zhongbiaohx_gg","http://www.gaztbw.gov.cn/jyxx/001003/001003004/secondpageJyMk.html",["name","ggstart_time","href",'info'],add_info(f1,{'gclx':"水利工程"}),f2],
    ["gcjs_shuili_gqita_da_bian_gg","http://www.gaztbw.gov.cn/jyxx/001003/001003002/secondpageJyMk.html",["name","ggstart_time","href",'info'],add_info(f1,{'gclx':"水利工程"}),f2],

    ["zfcg_zhaobiao_gg","http://www.gaztbw.gov.cn/jyxx/001004/001004001/secondpageJyMk.html",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_zhongbiao_gg","http://www.gaztbw.gov.cn/jyxx/001004/001004004/secondpageJyMk.html",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_biangeng_gg","http://www.gaztbw.gov.cn/jyxx/001004/001004002/secondpageJyMk.html",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_gqita_da_bian_gg","http://www.gaztbw.gov.cn/jyxx/001004/001004003/secondpageJyMk.html",["name","ggstart_time","href",'info'],f1,f2],

    ["jqita_gqita_zhao_bian_gg","http://www.gaztbw.gov.cn/jyxx/001008/001008001/secondpageJyMk.html",["name","ggstart_time","href",'info'],f1,f2],
    ["jqita_gqita_zhonghx_liu_gg","http://www.gaztbw.gov.cn/jyxx/001008/001008002/secondpageJyMk.html",["name","ggstart_time","href",'info'],f1,f2],

    ["zfcg_zhaobiao_danyilaiyuan_gg","http://www.gaztbw.gov.cn/jyxx/001004/001004005/secondpageJyMk.html",["name","ggstart_time","href",'info'],add_info(f1,{'zbfs':"单一来源"}),f2],



]
def work(conp,**args):
    est_meta(conp,data=data,diqu="江西省高安市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","jiangxi","gaoan"]

    work(conp=conp,headless=False,num=1)