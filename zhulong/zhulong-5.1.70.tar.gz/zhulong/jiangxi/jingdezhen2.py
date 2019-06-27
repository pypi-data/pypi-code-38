import json
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


from zhulong.util.etl import est_tbs, est_meta, est_html, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hengyang.gov.cn/jyxx/jsgc/zbgg_64796/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='jingdezhen2'

def f1(driver,num):
    locator = (By.XPATH, '//li[@class="wb-data-list"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url=driver.current_url

    if 'about.html' in url:
        cnum=1
    else:
        cnum=int(re.findall('/(\d+?).html',url)[0])


    if num !=cnum:

        if num == 1:
            url=re.sub('\/\d+.html','/about.html',url)
        else:
            url=re.sub('\/(\d+|(about)).html','/%s.html'%num,url)

        val = driver.find_element_by_xpath('//li[@class="wb-data-list"][1]//a').get_attribute('href')[-45:-20]
        driver.get(url)
        locator = (By.XPATH, "//li[@class='wb-data-list'][1]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    data = []
    lis = soup.find_all('li', class_='wb-data-list')

    for li in lis:

        href = li.find('a')['href']
        name = li.find('a')['title']
        ggstart_time = li.find('span',class_='wb-data-date').get_text()
        if 'http' in href:
            href = href
        else:
            href = 'http://jdzggzyjyzx.cn' + href

        diqu=re.findall('^\[.*?\]',name)
        if diqu:
            info=json.dumps({"diqu":diqu},ensure_ascii=False)
        else:
            info=None

        tmp = [name, ggstart_time, href,info]

        data.append(tmp)
    df=pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//li[@class="wb-data-list"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        page = driver.find_element_by_xpath('//*[@id="index"]').text
        total = int(page.strip().split('/')[1])
    except:
        total=1

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="article-info"][string-length()>100] | //div[@class="ewb-main"][string-length()>100]')

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
    div = soup.find('div',class_="ewb-detail-box")
    if not div:
        div=soup.find('div',class_='ewb-main')

    return div

data=[
    #
    ["gcjs_zhaobiao_shizheng_gg","http://jdzggzyjyzx.cn/jyxx/003001/003001001/about.html",["name","ggstart_time","href",'info'],add_info(f1,{"gclx":"房建及市政工程"}),f2],
    ["gcjs_gqita_da_bian_shizheng_gg","http://jdzggzyjyzx.cn/jyxx/003001/003001002/about.html",["name","ggstart_time","href",'info'],add_info(f1,{"gclx":"房建及市政工程"}),f2],
    ["gcjs_zhongbiaohx_shizheng_gg","http://jdzggzyjyzx.cn/jyxx/003001/003001004/about.html",["name","ggstart_time","href",'info'],add_info(f1,{"gclx":"房建及市政工程"}),f2],

    ["gcjs_zhaobiao_jiaotong_gg","http://jdzggzyjyzx.cn/jyxx/003002/003002001/about.html",["name","ggstart_time","href",'info'],add_info(f1,{"gclx":"交通工程"}),f2],
    ["gcjs_gqita_da_bian_jiaotong_gg","http://jdzggzyjyzx.cn/jyxx/003002/003002002/about.html",["name","ggstart_time","href",'info'],add_info(f1,{"gclx":"交通工程"}),f2],
    ["gcjs_zhongbiaohx_jiaotong_gg","http://jdzggzyjyzx.cn/jyxx/003002/003002003/about.html",["name","ggstart_time","href",'info'],add_info(f1,{"gclx":"交通工程"}),f2],

    ["gcjs_zhaobiao_shuili_gg","http://jdzggzyjyzx.cn/jyxx/003003/003003001/about.html",["name","ggstart_time","href",'info'],add_info(f1,{"gclx":"水利工程"}),f2],
    ["gcjs_gqita_da_bian_shuili_gg","http://jdzggzyjyzx.cn/jyxx/003003/003003001/about.html",["name","ggstart_time","href",'info'],add_info(f1,{"gclx":"水利工程"}),f2],
    ["gcjs_zhongbiaohx_shuili_gg","http://jdzggzyjyzx.cn/jyxx/003003/003003004/about.html",["name","ggstart_time","href",'info'],add_info(f1,{"gclx":"水利工程"}),f2],

    ["yiliao_zhaobiao_gg","http://jdzggzyjyzx.cn/jyxx/003009/003009001/about.html",["name","ggstart_time","href",'info'],f1,f2],
    ["yiliao_zhongbiao_gg","http://jdzggzyjyzx.cn/jyxx/003009/003009002/about.html",["name","ggstart_time","href",'info'],f1,f2],

    ["zfcg_zhaobiao_gg","http://jdzggzyjyzx.cn/jyxx/003005/003005001/about.html",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_biangeng_gg","http://jdzggzyjyzx.cn/jyxx/003005/003005002/about.html",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_gqita_da_bian_gg","http://jdzggzyjyzx.cn/jyxx/003005/003005003/about.html",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_zhongbiao_gg","http://jdzggzyjyzx.cn/jyxx/003005/003005004/about.html",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_zhaobiao_danyilaiyuan_gg","http://jdzggzyjyzx.cn/jyxx/003005/003005005/about.html",["name","ggstart_time","href",'info'],add_info(f1,{"zbfs":"单一来源"}),f2],

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="江西省景德镇市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':


    # conp=["postgres","since2015","192.168.3.171","jiangxi","jingdezhen2"]
    #
    # work(conp=conp,headless=False,num=1)

    driver=webdriver.Chrome()
    url='http://jdzggzyjyzx.cn/jyxx/003001/003001001/about.html'
    driver.get(url)
    f1(driver,2)