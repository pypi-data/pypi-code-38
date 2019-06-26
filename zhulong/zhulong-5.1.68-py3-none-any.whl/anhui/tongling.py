import pandas as pd  
import re 

from selenium import webdriver 
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_command,db_query
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 

import sys 
import time

import json
from zhulong.util.etl import est_tbs, est_meta, est_html, gg_existed, add_info

sys.setrecursionlimit(2000)

# driver=webdriver.Chrome()

# url="""http://ggzy.yzcity.gov.cn/yzweb/infodetail/?infoid=54f9755b-eb92-4f28-a454-cfcec6dce0d5&categoryNum=004001001001"""

# driver.get(url)


_name_='tongling'


def f1(driver,num):
    url = driver.current_url

    locator = (By.XPATH, '//*[@id="DataGrid1"]/tbody/tr[1]/td[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = re.findall('Paging=(\d+)', url)[0]

    main_url = url.rsplit('=', maxsplit=1)[0]

    if int(cnum) != num:
        val = driver.find_element_by_xpath('//*[@id="DataGrid1"]/tbody/tr[1]/td[2]/a').get_attribute('href')[-40:-20]
        url = main_url + '=' + str(num)

        driver.get(url)
        locator = (By.XPATH, '//*[@id="DataGrid1"]/tbody/tr[1]/td[2]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', id='DataGrid1')
    trs = div.find_all('tr')

    for tr in trs:
        try:
            tds = tr.find_all('td')
            href = tds[1].a['href']
            content = tds[1].a.get_text().strip()
            name = re.findall('(.+)\[', content)[0] if re.findall('(.+)\[', content) else content
            ggstart_time = tds[2].span.get_text()
        except:
            continue

        if 'http' in href:
            href = href
        else:
            href = 'http://ggzyjyzx.tl.gov.cn' + href

        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df


def f4(driver,num):
    url = driver.current_url

    locator = (By.XPATH, '//table[@class="moreinfocon"]/tbody/tr[1]/td[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = re.findall('Paging=(\d+)', url)[0]

    main_url = url.rsplit('=', maxsplit=1)[0]

    if int(cnum) != num:
        val = driver.find_element_by_xpath('//table[@class="moreinfocon"]/tbody/tr[1]/td[2]/a').get_attribute('href')[-40:-20]
        url = main_url + '=' + str(num)

        driver.get(url)
        try:
            locator = (By.XPATH, '//table[@class="moreinfocon"]/tbody/tr[1]/td[2]/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            driver.refresh()
            locator = (By.XPATH, '//table[@class="moreinfocon"]/tbody/tr[1]/td[2]/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', class_='moreinfocon')
    trs = div.find_all('tr')

    for tr in trs:

        tds = tr.find_all('td')
        href = tds[1].a['href']
        content = tds[1].a['title']
        # print(content)
        try:
            name = re.findall('(.+)\[', content)[0]
        except:
            name = content

        ggstart_time = tds[2].span.get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://ggzyjyzx.tl.gov.cn' + href

        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df

def f5(driver,num):
    url = driver.current_url
    locator = (By.XPATH, '//ul[@class="mored"]/li[1]/div/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = re.findall('Paging=(\d+)', url)[0]

    main_url = url.rsplit('=', maxsplit=1)[0]

    if int(cnum) != num:
        val = driver.find_element_by_xpath('//ul[@class="mored"]/li[1]/div/a').get_attribute('href')[-50:-25]
        url = main_url + '=' + str(num)
        driver.get(url)
        locator = (By.XPATH, '//ul[@class="mored"]/li[1]/div/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', class_='mored')
    trs = div.find_all('li')

    for li in trs:
        ggstart_time = li.i.get_text()
        ggstart_time = re.findall('\[(.+\])', ggstart_time)[0]
        href = li.div.a['href']
        name = li.div.a['title']

        if 'http' in href:
            href = href
        else:
            if 'zyx' in url:
                href = 'http://ggzyjyzx.tl.gov.cn' + href
            elif 'yaq' in url:
                href = 'http://ggzyjyzx.tl.gov.cn' + href
            else:
                href=href
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df



def f2(driver):
    locator = (By.XPATH,
       '//*[@id="DataGrid1"]/tbody/tr[1]/td[2]/a | '
       '//table[@class="moreinfocon"]/tbody/tr[1]/td[2]/a |'
       ' //ul[@class="mored"]/li[1]/div/a')

    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        page = driver.find_element_by_xpath('//div[@class="pageText xxxsHidden"][1] | //td[@class="huifont"]').text
        total = re.findall('/(\d+)', page)[0]
        total = int(total)
    except:
        total = 1

    driver.quit()
    return total



def f3(driver,url):
    driver.get(url)
    locator = (
     By.XPATH, '//table[@id="tblInfo"] | //div[contains(@id,"menutab") and (not(@style) or @style="")] | //div[@class="container clearfix"]')
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    except:
        if '404' in driver.title:
            return '404'
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

    if 'tlsggzy' in url:
        div = soup.find('div', attrs={'id': re.compile('menutab_6_\d'), 'style': ''})
        if div == None:
            div = soup.find('div', class_="container clearfix")

    elif 'yaq' in url:
        div = soup.find('table', id="tblInfo")  # 枞阳县、义安区
    elif 'zyx' in url:
        div = soup.find('table', id="tblInfo")  # 枞阳县、义安区
    else:
        div = soup.find('td', class_="infodetail")

    if div == None:
        raise ValueError

    return div


data = [
    #
    ["gcjs_zhaobiao_gg", "http://ggzyjyzx.tl.gov.cn/tlsggzy/ZtbInfo/zhaobiao.aspx?categorynum=006001001&Paging=1",['name', 'ggstart_time', 'href',"info"],add_info(f1,{"diqu":"市级"}),f2],
    ["gcjs_zhongbiaohx_gg", "http://ggzyjyzx.tl.gov.cn/tlsggzy/ZtbInfo/zhaobiao.aspx?categorynum=006001003&Paging=1", ['name', 'ggstart_time', 'href',"info"],add_info(f1,{"diqu":"市级"}),f2],
    ["gcjs_zhongbiao_gg", "http://ggzyjyzx.tl.gov.cn/tlsggzy/ZtbInfo/zhaobiao.aspx?categorynum=006001004&Paging=1",  ['name',  'ggstart_time', 'href',"info"],add_info(f1,{"diqu":"市级"}),f2],
    ["gcjs_liubiao_gg", "http://ggzyjyzx.tl.gov.cn/tlsggzy/ZtbInfo/zhaobiao.aspx?categorynum=006001006&Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f1,{"diqu":"市级"}),f2],
    #######补充公告实为变更
    ["gcjs_biangeng_gg", "http://ggzyjyzx.tl.gov.cn/tlsggzy/ZtbInfo/zhaobiao.aspx?categorynum=006001002&Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f1,{"diqu":"市级"}),f2],

    ["gcjs_dingdianchouqian_zhaobiao_gg", "http://ggzyjyzx.tl.gov.cn/tlsggzy/ZtbInfo/zhaobiao.aspx?categorynum=006002001&Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f1,{"diqu":"市级","zbfs":"定点抽签"}),f2],
    ["gcjs_dingdianchouqian_zhongbiao_gg","http://ggzyjyzx.tl.gov.cn/tlsggzy/ZtbInfo/zhaobiao.aspx?categorynum=006002004&Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f1,{"diqu":"市级","zbfs":"定点抽签"}),f2],
    ["gcjs_dingdianchouqian_biangeng_gg","http://ggzyjyzx.tl.gov.cn/tlsggzy/ZtbInfo/zhaobiao.aspx?categorynum=006002002&Paging=1", ['name',  'ggstart_time', 'href',"info"],add_info(f1,{"diqu":"市级","zbfs":"定点抽签"}),f2],

    ["zfcg_zhaobiao_gg", "http://ggzyjyzx.tl.gov.cn/tlsggzy/ZtbInfo/zhaobiao.aspx?categorynum=007001001&Paging=1", ['name',  'ggstart_time', 'href',"info"],add_info(f1,{"diqu":"市级"}),f2],


    ["zfcg_biangeng_gg", "http://ggzyjyzx.tl.gov.cn/tlsggzy/ZtbInfo/zhaobiao.aspx?categorynum=007001002&Paging=1", ['name',  'ggstart_time', 'href',"info"],add_info(f1,{"diqu":"市级"}),f2],
    ["zfcg_zhongbiao_gg", "http://ggzyjyzx.tl.gov.cn/tlsggzy/ZtbInfo/zhaobiao.aspx?categorynum=007001004&Paging=1", ['name',  'ggstart_time', 'href',"info"],add_info(f1,{"diqu":"市级"}),f2],
    ["zfcg_liubiao_gg", "http://ggzyjyzx.tl.gov.cn/tlsggzy/ZtbInfo/zhaobiao.aspx?categorynum=007001006&Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f1,{"diqu":"市级"}),f2],
    ["zfcg_zhaobiao_danyilaiyuan_gg", "http://ggzyjyzx.tl.gov.cn/tlsggzy/ZtbInfo/zhaobiao.aspx?categorynum=007004001&Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f1,{"diqu":"市级","zbfs":"单一来源"}),f2],
    #
    ["zfcg_feigong_zhaobiao_gg", "http://ggzyjyzx.tl.gov.cn/tlsggzy/ZtbInfo/zhaobiao.aspx?categorynum=007002001&Paging=1", ['name',  'ggstart_time', 'href',"info"],add_info(f1,{"diqu":"市级","zbfs":"非公开招标"}),f2],
    ["zfcg_feigong_biangeng_gg", "http://ggzyjyzx.tl.gov.cn/tlsggzy/ZtbInfo/zhaobiao.aspx?categorynum=007002002&Paging=1", ['name',  'ggstart_time', 'href',"info"],add_info(f1,{"diqu":"市级","zbfs":"非公开招标"}),f2],
    ["zfcg_feigong_zhongbiao_gg", "http://ggzyjyzx.tl.gov.cn/tlsggzy/ZtbInfo/zhaobiao.aspx?categorynum=007002004&Paging=1", ['name',  'ggstart_time', 'href',"info"],add_info(f1,{"diqu":"市级","zbfs":"非公开招标"}),f2],
    ["zfcg_feigong_liubiao_gg", "http://ggzyjyzx.tl.gov.cn/tlsggzy/ZtbInfo/zhaobiao.aspx?categorynum=007002006&Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f1,{"diqu":"市级","zbfs":"非公开招标"}),f2],


    ["gcjs_yucai_gg", "http://ggzyjyzx.tl.gov.cn/tlsggzy/gcjs/006003/?Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f4,{"diqu":"市级"}),f2],
    ["zfcg_yucai_gg", "http://ggzyjyzx.tl.gov.cn/tlsggzy/zfcg/007003/?Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f4,{"diqu":"市级"}),f2],


    ["gcjs_zhaobiao_yaq_gg", "http://yaq.tlzbcg.com/yaqztb/jyxx/008001/008001001/?Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f5,{"diqu":"义安区"}),f2],
    ["gcjs_zhongbiaohx_yaq_gg", "http://yaq.tlzbcg.com/yaqztb/jyxx/008001/008001003/?Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f5,{"diqu":"义安区"}),f2],
    ["gcjs_zhongbiao_yaq_gg", "http://yaq.tlzbcg.com/yaqztb/jyxx/008001/008001004/?Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f5,{"diqu":"义安区"}),f2],
    ["gcjs_liubiao_yaq_gg", "http://yaq.tlzbcg.com/yaqztb/jyxx/008001/008001005/?Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f5,{"diqu":"义安区"}),f2],

    ["zfcg_zhaobiao_yaq_gg", "http://yaq.tlzbcg.com/yaqztb/jyxx/008002/008002001/?Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f5,{"diqu":"义安区"}),f2],

    ["zfcg_biangeng_yaq_gg", "http://yaq.tlzbcg.com/yaqztb/jyxx/008002/008002002/?Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f5,{"diqu":"义安区"}),f2],
    ["zfcg_zhongbiao_yaq_gg", "http://yaq.tlzbcg.com/yaqztb/jyxx/008002/008002003/?Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f5,{"diqu":"义安区"}),f2],
    ["zfcg_liubiao_yaq_gg", "http://yaq.tlzbcg.com/yaqztb/jyxx/008002/008002004/?Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f5,{"diqu":"义安区"}),f2],


    ###以下网址已归档至市级

    ["gcjs_zhaobiao_zyx_gg", "http://zyx.tlzbcg.com/zyxztb/jyxx/008001/008001001/?Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f5,{"diqu":"枞阳县"}),f2],
    ["gcjs_zhongbiaohx_zyx_gg", "http://zyx.tlzbcg.com/zyxztb/jyxx/008001/008001003/?Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f5,{"diqu":"枞阳县"}),f2],
    ["gcjs_zhongbiao_zyx_gg", "http://zyx.tlzbcg.com/zyxztb/jyxx/008001/008001004/?Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f5,{"diqu":"枞阳县"}),f2],
    ["gcjs_liubiao_zyx_gg", "http://zyx.tlzbcg.com/zyxztb/jyxx/008001/008001005/?Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f5,{"diqu":"枞阳县"}),f2],

    ["zfcg_zhaobiao_zyx_gg", "http://zyx.tlzbcg.com/zyxztb/jyxx/008002/008002001/?Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f5,{"diqu":"枞阳县"}),f2],
    ["zfcg_biangeng_zyx_gg", "http://zyx.tlzbcg.com/zyxztb/jyxx/008002/008002002/?Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f5,{"diqu":"枞阳县"}),f2],
    ["zfcg_zhongbiao_zyx_gg", "http://zyx.tlzbcg.com/zyxztb/jyxx/008002/008002003/?Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f5,{"diqu":"枞阳县"}),f2],
    ["zfcg_zhaobiao_danyilaiyuan_zyx_gg", "http://zyx.tlzbcg.com/zyxztb/jyxx/008002/008002004/?Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f5,{"diqu":"枞阳县","zbfs":"单一来源"}),f2],
    ["zfcg_liubiao_zyx_gg", "http://zyx.tlzbcg.com/zyxztb/jyxx/008002/008002005/?Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f5,{"diqu":"枞阳县"}),f2],

    ["qsy_zhaobiao_zyx_gg", "http://zyx.tlzbcg.com/zyxztb/jyxx/008005/008005001/?Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f5,{"diqu":"枞阳县"}),f2],
    ["qsy_zhongbiao_zyx_gg", "http://zyx.tlzbcg.com/zyxztb/jyxx/008005/008005004/?Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f5,{"diqu":"枞阳县"}),f2],
    ["qsy_biangeng_zyx_gg", "http://zyx.tlzbcg.com/zyxztb/jyxx/008005/008005002/?Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f5,{"diqu":"枞阳县"}),f2],

    ["qsy_liubiao_zyx_gg", "http://zyx.tlzbcg.com/zyxztb/jyxx/008005/008005005/?Paging=1",['name',  'ggstart_time', 'href',"info"],add_info(f5,{"diqu":"枞阳县"}),f2],


]

#2019-06-25
#域名变更 http://ggzyjyzx.tl.gov.cn


def work(conp,**args):
    est_meta(conp,data=data,diqu="安徽省铜陵市",**args)
    est_html(conp,f=f3,**args)

if __name__=='__main__':



    work(conp=["postgres","since2015","192.168.4.175","anhui","tongling"])
