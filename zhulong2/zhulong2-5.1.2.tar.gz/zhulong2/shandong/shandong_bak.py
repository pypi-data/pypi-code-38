import random
import time

import pandas as pd
import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zhulong2.util.fake_useragent import UserAgent
import requests
from zhulong2.util.etl import est_tbs, est_meta, est_html, gg_existed, est_gg, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hefei.gov.cn/jyxx/002001/002001002/moreinfo_jyxx.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_='shandong_shandong'



def f1(driver,num):
    proxies_data = webdriver.DesiredCapabilities.CHROME
    proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
    if proxies_chromeOptions:
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    else:
        proxies = {}

    locator = (By.XPATH, '(//td[@class="Font9"])[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url=driver.current_url

    cookies = driver.get_cookies()
    COOKIES = {}
    for cookie in cookies:
        COOKIES[cookie['name']] = cookie['value']

    ua=UserAgent()
    colcode=re.findall('colcode=(\d+)$',url)[0] if re.findall('colcode=(\d+)$',url) else None
    form_data={
        "colcode": colcode,
        "curpage": num,
    }

    if 'channelall' in url:
        req_url=re.findall('(.+)\?colcode',url)[0]
    else:
        req_url=url
        form_data.pop('colcode')

    headers = {
        "Referer": url,
        "User-Agent": ua.chrome
    }

    time.sleep(random.random()+0.5)
    req=requests.post(req_url,data=form_data,headers=headers,proxies=proxies,cookies=COOKIES,timeout=15)
    if req.status_code != 200:
        # print(req.status_code)
        raise ValueError('Error response status_code %s'%req.status_code)
    html=req.text

    data = []

    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find_all('td', class_='Font9')
    for i in range(len(div)-1):
        td=div[i]
        if len(td) == 0:
            continue
        href=td.a['href']
        if 'http' in href:
            href=href
        else:
            href="http://www.ccgp-shandong.gov.cn"+href
        name=td.a['title']
        td.a.extract()
        ggstart_time=td.get_text().strip()
        tmp = [name, ggstart_time,href]

        data.append(tmp)

    df=pd.DataFrame(data=data)
    df['info']=None
    return df


def f2(driver):

    locator = (By.XPATH, '(//td[@class="Font9"])[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('(//td[@class="Font9"])[last()]//strong').text
    # print(page)
    total = re.findall('/(\d+)', page)[0]
    total = int(total)

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '(//td[@bgcolor="#FFFFFF"])[3][string-length()>10]')

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

    div = soup.find_all('td', attrs={'bgcolor': '#FFFFFF'})[2].parent.parent
    if div == None:
        raise ValueError

    return div




data=[
        #
    ["zfcg_zhaobiao_diqu1_gg", "http://www.ccgp-shandong.gov.cn/sdgp2017/site/channelall.jsp?colcode=0301",['name', 'ggstart_time', 'href', 'info'], add_info(f1,{"diqu":"省直"}), f2],
    ["zfcg_zhaobiao_diqu2_gg", "http://www.ccgp-shandong.gov.cn/sdgp2017/site/channelall.jsp?colcode=0303",['name', 'ggstart_time', 'href', 'info'], add_info(f1,{"diqu":"市县"}), f2],
    ["zfcg_zhongbiao_diqu1_gg", "http://www.ccgp-shandong.gov.cn/sdgp2017/site/channelall.jsp?colcode=0302",['name', 'ggstart_time', 'href', 'info'], add_info(f1,{"diqu":"省直"}), f2],
    ["zfcg_zhongbiao_diqu2_gg", "http://www.ccgp-shandong.gov.cn/sdgp2017/site/channelall.jsp?colcode=0304",['name', 'ggstart_time', 'href', 'info'], add_info(f1,{"diqu":"市县"}), f2],
    ["zfcg_biangeng_gg", "http://www.ccgp-shandong.gov.cn/sdgp2017/site/channelall.jsp?colcode=0305",['name', 'ggstart_time', 'href', 'info'], f1, f2],
    ["zfcg_liubiao_gg", "http://www.ccgp-shandong.gov.cn/sdgp2017/site/channelall.jsp?colcode=0306",['name', 'ggstart_time', 'href', 'info'], f1, f2],
    ["zfcg_zgys_gg", "http://www.ccgp-shandong.gov.cn/sdgp2017/site/channelall.jsp?colcode=0307",['name', 'ggstart_time', 'href', 'info'], f1, f2],
    #
    ["zfcg_yucai_diqu1_gg", "http://www.ccgp-shandong.gov.cn/sdgp2017/site/listneedall.jsp",['name', 'ggstart_time', 'href', 'info'],add_info(f1,{"diqu":"省直"}), f2],
    ["zfcg_yanshou_diqu1_gg", "http://www.ccgp-shandong.gov.cn/sdgp2017/site/listchkall.jsp",['name', 'ggstart_time', 'href', 'info'], add_info(f1,{"diqu":"省直"}), f2],
    ["zfcg_gqita_dingdian_gg", "http://www.ccgp-shandong.gov.cn/sdgp2017/site/listcontractall.jsp?contractType=2",['name', 'ggstart_time', 'href', 'info'],add_info(f1,{"tag":"协议供货|定点采购"}), f2],
    ["zfcg_yucai_diqu2_gg", "http://www.ccgp-shandong.gov.cn/sdgp2017/site/channelallshow.jsp?colcode=2504",['name', 'ggstart_time', 'href', 'info'], add_info(f1,{"diqu":"市县"}), f2],
    ["zfcg_yanshou_diqu2_gg", "http://www.ccgp-shandong.gov.cn/sdgp2017/site/channelallshow.jsp?colcode=2506",['name', 'ggstart_time', 'href', 'info'],add_info(f1,{"diqu":"市县"}), f2],

    #
    ["zfcg_gqita_jinkou_gg", "http://www.ccgp-shandong.gov.cn/sdgp2017/site/channelall.jsp?colcode=2101",['name', 'ggstart_time', 'href', 'info'], add_info(f1,{"tag":"进口产品"}), f2],
    ["zfcg_zhaobiao_danyilaiyuan_diqu1_gg", "http://www.ccgp-shandong.gov.cn/sdgp2017/site/channelall.jsp?colcode=2102",['name', 'ggstart_time', 'href', 'info'], add_info(f1,{"zbfs":"单一来源","diqu":"省直"}), f2],
    ["zfcg_gqita_ppp_gg", "http://www.ccgp-shandong.gov.cn/sdgp2017/site/channelall.jsp?colcode=2103",['name', 'ggstart_time', 'href', 'info'], add_info(f1,{"tag":"PPP项目"}), f2],
    ["zfcg_zhaobiao_danyilaiyuan_diqu2_gg", "http://www.ccgp-shandong.gov.cn/sdgp2017/site/channelall.jsp?colcode=2106",['name', 'ggstart_time', 'href', 'info'], add_info(f1,{"zbfs":"单一来源","diqu":"市县"}), f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="山东省山东",**args)
    est_html(conp,f=f3,**args)

if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","lch","shandong_shandong"]

    work(conp=conp,pageloadtime=60)