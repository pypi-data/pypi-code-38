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


from zhulong2.util.etl import est_tbs, est_meta, est_html, est_gg, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hengyang.gov.cn/jyxx/jsgc/zbgg_64796/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='hunan_changsha'


def f1(driver,num):
    locator = (By.XPATH,
               '(//div[@class="item no-date-toshow"][1]//a)[1] | (//div[@class="ui divided items page-placard"]/div[@class="item"][1]//a)[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = url.rsplit('=', maxsplit=1)[1]
    main_url = url.rsplit('=', maxsplit=1)[0]

    if int(cnum) != num:
        val = \
            driver.find_element_by_xpath(
                '(//div[@class="item no-date-toshow"][1]//a)[1] | (//div[@class="ui divided items page-placard"]/div[@class="item"][1]//a)[1]').get_attribute(
                'href').rsplit(
                '/', maxsplit=1)[1]

        url_ = main_url + '=%d' % num
        driver.get(url_)

        locator = (By.XPATH,
                   '(//div[@class="item no-date-toshow"][1]//a)[1][not(contains(@href,"%s"))] | (//div[@class="ui divided items page-placard"]/div[@class="item"][1]//a)[1][not(contains(@href,"%s"))]' % (
                   val, val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    divs = soup.find_all('div', class_='item no-date-toshow')

    if not divs:
        divs = soup.find('div', class_='ui divided items page-placard').find_all('div', class_='item', recursive=False)
    for div in divs:
        name = div.find_all('a')[0]['title']
        href = div.find_all('a')[0]['href']
        ggstart_time = div.find_all('a')[1].span.get_text()
        ggstart_time = re.findall('\d+-\d+-\d+', ggstart_time)[0]
        meta = div.find('div', class_="meta")
        gg_type = meta.find('div', attrs={'title': '公告类别'}).get_text().strip()
        cg_type = meta.find('div', attrs={'title': '采购方式'}).get_text().strip()
        address = meta.find('div', attrs={'title': '所属地区'}).get_text().strip()

        money = meta.find('span', id="bidMoney").get_text().strip()
        company = meta.find('span', class_="agent").get_text().strip()
        company = re.findall(' .+? ', company)[0].strip() if re.findall(' .+? ', company) else None
        if 'http' in href:
            href = href
        else:
            href = 'http://changs.ccgp-hunan.gov.cn' + href
        
        info={'gg_type':gg_type,'zbfs':cg_type,'money':money,'company':company,'diqu':address}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time, href,info]
        data.append(tmp)

    df=pd.DataFrame(data=data)
    
    return df


def f2(driver):
    locator = (By.XPATH, '(//div[@class="item no-date-toshow"][1]//a)[1] | (//div[@class="ui divided items page-placard"]/div[@class="item"][1]//a)[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('//a[@class="item disabled"]').text
    total = re.findall('共有(.+)页', page)[0].strip()
    total = int(total)
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)
    try:
        locator = (By.XPATH, '//div[@class="article-body"][string-length()>10]')

        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    except:
        if "404 Not Found" in driver.page_source:
            return 404
        else:
            raise TimeoutError
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
    div = soup.find('div',class_="article-body")
    if div == None:
        raise ValueError

    return div



data=[

    ["zfcg_gqita_diqu1_gg","http://changs.ccgp-hunan.gov.cn/gp/cms/11/search.do?basic_area=changsha&categoryId=217&from=changs&pageNo=1",["name", "ggstart_time",  "href",'info'],f1,f2],
    ["zfcg_gqita_diqu2_gg","http://changs.ccgp-hunan.gov.cn/gp/cms/11/search.do?basic_area=quxian&categoryId=217&from=changs&pageNo=1",["name", "ggstart_time",  "href",'info'],f1,f2],

    ["zfcg_gqita_da_bian_diqu2_gg","http://changs.ccgp-hunan.gov.cn/gp/cms/11/search.do?basic_area=quxian&categoryId=189&from=changs&pageNo=1",["name", "ggstart_time",  "href",'info'],f1,f2],
    ["zfcg_gqita_da_bian_diqu1_gg","http://changs.ccgp-hunan.gov.cn/gp/cms/11/search.do?basic_area=changsha&categoryId=189&from=changs&pageNo=1",["name", "ggstart_time",  "href",'info'],f1,f2],

    ["zfcg_zhongbiao_1_diqu1_gg","http://changs.ccgp-hunan.gov.cn/gp/cms/11/search.do?basic_area=changsha&categoryId=203&from=changs&pageNo=1",["name", "ggstart_time",  "href",'info'],f1,f2],
    ["zfcg_zhongbiao_1_diqu2_gg","http://changs.ccgp-hunan.gov.cn/gp/cms/11/search.do?basic_area=quxian&categoryId=203&from=changs&pageNo=1",["name", "ggstart_time",  "href",'info'],f1,f2],

    ["zfcg_zhongbiao_2_diqu1_gg","http://changs.ccgp-hunan.gov.cn/gp/cms/11/search.do?basic_area=changsha&categoryId=204&from=changs&pageNo=1",["name", "ggstart_time", "href",'info'],f1,f2],
    ["zfcg_zhongbiao_2_diqu2_gg","http://changs.ccgp-hunan.gov.cn/gp/cms/11/search.do?basic_area=quxian&categoryId=204&from=changs&pageNo=1",["name", "ggstart_time", "href",'info'],f1,f2],

    ["zfcg_liubiao_diqu1_gg","http://changs.ccgp-hunan.gov.cn/gp/cms/11/search.do?basic_area=changsha&categoryId=208&from=changs&pageNo=1",["name", "ggstart_time",  "href",'info'],f1,f2],
    ["zfcg_liubiao_diqu2_gg","http://changs.ccgp-hunan.gov.cn/gp/cms/11/search.do?basic_area=quxian&categoryId=208&from=changs&pageNo=1",["name", "ggstart_time",  "href",'info'],f1,f2],

    ["zfcg_zhongzhi_diqu1_gg","http://changs.ccgp-hunan.gov.cn/gp/cms/11/search.do?basic_area=changsha&categoryId=219&from=changs&pageNo=1",["name", "ggstart_time", "href",'info'],f1,f2],
    ["zfcg_zhongzhi_diqu2_gg","http://changs.ccgp-hunan.gov.cn/gp/cms/11/search.do?basic_area=quxian&categoryId=219&from=changs&pageNo=1",["name", "ggstart_time", "href",'info'],f1,f2],

    ["zfcg_zgys_diqu1_gg","http://changs.ccgp-hunan.gov.cn/gp/cms/11/search.do?basic_area=changsha&categoryId=222&from=changs&pageNo=1",["name", "ggstart_time",  "href",'info'],f1,f2],
    ["zfcg_zgys_diqu2_gg","http://changs.ccgp-hunan.gov.cn/gp/cms/11/search.do?basic_area=quxian&categoryId=222&from=changs&pageNo=1",["name", "ggstart_time", "href",'info'],f1,f2],

    ["zfcg_zhaobiao_feigong_diqu1_gg","http://changs.ccgp-hunan.gov.cn/gp/cms/11/search.do?basic_area=changsha&categoryId=218&from=changs&pageNo=1",["name", "ggstart_time",  "href",'info'],f1,f2],
    ["zfcg_zhaobiao_feigong_diqu2_gg","http://changs.ccgp-hunan.gov.cn/gp/cms/11/search.do?basic_area=quxian&categoryId=218&from=changs&pageNo=1",["name", "ggstart_time",  "href",'info'],f1,f2],

    ["zfcg_zhaobiao_diqu1_gg","http://changs.ccgp-hunan.gov.cn/gp/cms/11/search.do?basic_area=changsha&categoryId=188&from=changs&pageNo=1",["name", "ggstart_time",  "href",'info'],f1,f2],
    ["zfcg_zhaobiao_diqu2_gg","http://changs.ccgp-hunan.gov.cn/gp/cms/11/search.do?basic_area=quxian&categoryId=188&from=changs&pageNo=1",["name", "ggstart_time", "href",'info'],f1,f2],

    ["zfcg_zhaobiao_jingjia_diqu2_gg","http://changs.ccgp-hunan.gov.cn/gp/cms/11/search.do?basic_area=quxian&categoryId=202&from=changs&pageNo=1",["name", "ggstart_time", "href",'info'],f1,f2],
    ["zfcg_zhaobiao_jingjia_jieguo_diqu2_gg","http://changs.ccgp-hunan.gov.cn/gp/cms/11/search.do?basic_area=quxian&categoryId=205&from=changs&pageNo=1",["name", "ggstart_time", "href",'info'],f1,f2],

    ### f1 中 info中有diqu,zbfs,不用在此加info
]

def work(conp,**args):
    est_meta(conp,data=data,diqu="湖南省长沙市",**args)
    est_html(conp,f=f3,**args)



if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","lch","hunan_changsha"]

    work(conp=conp,pageloadtimeout=80,pageloadstrategy='none')