from pprint import pprint
import time
from collections import OrderedDict

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from zhulong.util.etl import est_tbs, est_meta, est_html, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://www.gzzbtbzx.com/more.asp?id=5&city=1"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_ = 'ganzhou'


def f1(driver, num):
    url = driver.current_url

    if 'id' in url:
        locator = (By.XPATH, '//td[@bgcolor="#DFDFDF"]/table[3]/tbody/tr/td/a')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        main_url = url.rsplit('=', maxsplit=1)[0]
        cnum = url.rsplit('=', maxsplit=1)[1]
        cnum = int(cnum)
        if cnum != num:
            c_url = main_url + '=' + str(num)
            val = driver.find_element_by_xpath('//td[@bgcolor="#DFDFDF"]/table[3]/tbody/tr/td/a').get_attribute('href')[-10:]

            driver.get(c_url)

            locator = (By.XPATH, '//td[@bgcolor="#DFDFDF"]/table[3]/tbody/tr/td/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        df = parse_1(driver)

        return df

    elif 'dq' in url:
        locator = (By.XPATH, "//td[@bgcolor='#DFDFDF']/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[4]/td/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        main_url = url.rsplit('=', maxsplit=1)[0]
        cnum = url.rsplit('=', maxsplit=1)[1]
        cnum = int(cnum)
        if cnum != num:
            c_url = main_url + '=' + str(num)
            val = driver.find_element_by_xpath(
                "//td[@bgcolor='#DFDFDF']/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[4]/td/a").get_attribute('href')[-10:]
            driver.get(c_url)
            locator = (By.XPATH,
                       '//td[@bgcolor="#DFDFDF"]/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[4]/td/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        df = parse_2(driver)

        return df


def parse_1(driver):
    main_url = driver.current_url
    main_url = main_url.rsplit('/', maxsplit=1)[0]
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find('td', attrs={'bgcolor': '#DFDFDF'})
    tables = content.find_all('table')
    for i in range(2, len(tables) - 1):
        table = tables[i]
        tr = table.find('tr')
        tds = tr.find_all('td')
        href = tds[0].a['href']
        if 'http' in href:
            href = href
        else:
            href = main_url + '/' + href
        name = tds[0].a.get_text()
        ggstart_time = tds[1].get_text()
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def parse_2(driver):
    main_url = driver.current_url

    data = []
    main_url = main_url.rsplit('/', maxsplit=1)[0]

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find('td', attrs={'bgcolor': '#DFDFDF'})
    table = content.find_all('table')
    table = table[1]
    trss = table.find('table').find('table')
    trs = trss.find_all('tr')

    for i in range(3, len(trs), 2):
        tr = trs[i]
        tds = tr.find_all('td')
        href = tds[0].a['href']
        if 'http' in href:
            href = href
        else:
            href = main_url + '/' + href
        name = tds[0].a.get_text()
        ggstart_time = tds[2].get_text()
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//td[@bgcolor="#DFDFDF"]/table[3]/tbody/tr/td/a | '
                         '//td[@bgcolor="#DFDFDF"]/table[2]/tbody/tr/td/table[1]/tbody/tr/td/table/tbody/tr[4]/td[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        total = driver.find_element_by_xpath('//td[@bgcolor="#DFDFDF"]/table[last()]/tbody/tr[last()]/td/b[1]').text
    except:
        try:
            total = driver.find_element_by_xpath('//select[@name="page"]/option[last()]').text
        except:
            total = 1

    total = int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//table[@width="95%"][string-length()>10] | /html/body/table[@bgcolor="#FFFFFF"][string-length()>10]')

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
    div = soup.find('table', width="95%")
    if div == None:
        div=soup.find('body').find('table', bgcolor='#FFFFFF', recursive=False)

    return div


def get_data():
    data = []

    ggtype1 = OrderedDict([("zhaobiao", "2"), ("gqita_bumen", "5"), ("zhongbiao", "3")])

    adtype1 = OrderedDict([('市本级', '1'), ("章贡区", "20"), ("赣县", "2"), ("南康", "10"), ("信丰", "9"),
                           ('大余', '4'), ('上犹', '11'), ('崇义', '7'), ('安远', '13'), ('龙南', '6'),
                           ('全南', '15'), ('定南', '16'), ('兴国', '17'), ('宁都', '5'), ('于都', '3'),
                           ('瑞金', '12'), ('会昌', '18'), ('寻乌', '8'), ('石城', '14')])

    adtype2 = OrderedDict([('市本级', '1'), ("章贡区", "20"), ("赣县", "2"), ("南康", "10"), ("信丰", "9"),
                           ('大余', '4'), ('上犹', '11'), ('崇义', '7'), ('安远', '13'), ('龙南', '6'),
                           ('全南', '15'), ('定南', '16'), ('兴国', '17'), ('宁都', '5'), ('于都', '3'),
                           ('瑞金', '12'), ('会昌', '18'), ('寻乌', '8'), ('石城', '14'), ('开发区', '19')])

    ##gcjs_zhaobiao
    for w1 in adtype1.keys():
        href = "http://gcjs.gzzbtbzx.com:88/zbgg/more_ze.asp?keyword=&dq={}&cut=&page=1".format(adtype1[w1])
        tmp = ["gcjs_zhaobiao_diqu%s_gg" % ( adtype1[w1]), href, ["name", "ggstart_time", "href", 'info'],
               add_info(f1, {"diqu": w1}), f2]
        data.append(tmp)

    #gcjs_zhongbiaohx
    for w1 in adtype1.keys():
        href = "http://www.gzzbtbzx.com/more.asp?id=13&city=%s&page=1" % (adtype1[w1])
        tmp = ["gcjs_zhongbiaohx_diqu%s_gg" % ( adtype1[w1]), href, ["name", "ggstart_time", "href", 'info'],
               add_info(f1, {"diqu": w1}), f2]
        data.append(tmp)

    ##gcjs_da_bian
    for w1 in adtype1.keys():
        href = "http://www.gzzbtbzx.com/more.asp?id=41&city=%s&page=1" % (adtype1[w1])
        tmp = ["gcjs_gqita_da_bian_diqu%s_gg" % ( adtype1[w1]), href, ["name", "ggstart_time", "href", 'info'],
               add_info(f1, {"diqu": w1}), f2]
        data.append(tmp)


    ##zfcg
    for w1 in ggtype1.keys():
        for w2 in adtype2.keys():
            href = "http://www.gzzbtbzx.com/more.asp?id=%s&city=%s&page=1" % (ggtype1[w1], adtype2[w2])
            tmp = ["zfcg_%s_diqu%s_gg" % (w1, adtype2[w2]), href, ["name", "ggstart_time", "href", 'info'],
                   add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)

    remove_arr = ["gcjs_zhaobiao_diqu1_gg", "zfcg_gqita_bumen_diqu4_gg", 'zfcg_gqita_bumen_diqu7_gg',
                  'zfcg_gqita_bumen_diqu13_gg','zfcg_gqita_bumen_diqu15_gg', 'zfcg_gqita_bumen_diqu5_gg',
                  'zfcg_gqita_bumen_diqu12_gg', 'zfcg_gqita_bumen_diqu18_gg','zfcg_gqita_bumen_diqu8_gg']


    data1 = data.copy()
    for w in data:
        if w[0] in remove_arr: data1.remove(w)

    data1.append(["gcjs_zhaobiao_diqu1_gg", "http://www.gzzbtbzx.com/more.asp?id=12&city=1&page=1",
                  ["name", "ggstart_time", "href", 'info'], add_info(f1, {"diqu": '市本级'}), f2], )
    return data1


data = get_data()
#pprint(data)


def work(conp, **args):
    est_meta(conp, data=data, diqu="江西省赣州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "jiangxi", "ganzhou"]

    work(conp=conp,headless=False,num=1,cdc_total=2)
    # url='http://gcjs.gzzbtbzx.com:88/zbgg/list_url.asp?id=17296&url1=../file_announce/FYDSG110929161935wb.htm'
    # driver=webdriver.Chrome()
    # div=f3(driver,url)
    # print(div)