import json

from collections import OrderedDict
from pprint import pprint

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

_name_ = 'zhixiashi_beijing'


def f1(driver, num):
    locator = (By.XPATH, '//iframe[@id="main"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    driver.switch_to.frame('main')
    locator = (By.XPATH, '//table[@id="MyGridView1"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath('//div[@class="gridview_PagerRow"]/div').text
    cnum = re.findall('页码：(\d+)/\d+', cnum)[0]

    if int(cnum) != num:
        val = driver.find_element_by_xpath(
            '//table[@id="MyGridView1"]//tr[2]//a').get_attribute('href')[-40:]

        locator = (
            By.XPATH, '//div[@class="gridview_PagerRow"]//input[@type="text"]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        inp=driver.find_element_by_xpath('//div[@class="gridview_PagerRow"]//input[@type="text"]')
        inp.click()
        inp.clear()
        time.sleep(0.5)
        driver.find_element_by_xpath('//div[@class="gridview_PagerRow"]//input[@type="text"]').send_keys(str(num),Keys.ENTER)

        locator = (
            By.XPATH, "//table[@id='MyGridView1']//tr[2]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("table", id="MyGridView1")
    dls = div.find_all("tr")[1:]

    data = []
    for dl in dls:
        tds=dl.find_all('td')

        if len(tds) == 4:
            procode=tds[0].get_text().strip()
            dw=tds[2].get_text().strip()
            info=json.dumps({'procode':procode,'dw':dw},ensure_ascii=False)
        elif len(tds) == 3:

            if div.find('tr').find('td').get_text().strip() == "工程编号":

                procode = tds[0].get_text().strip()
                info = json.dumps({'procode': procode}, ensure_ascii=False)
            else:
                dw = tds[1].get_text().strip()
                info = json.dumps({ 'dw': dw}, ensure_ascii=False)

        elif len(tds) == 5:
            procode = tds[0].get_text().strip()
            laiyuan = tds[-2].get_text().strip()
            gctype=tds[2].get_text().strip()
            info = json.dumps({'gctype':gctype,'procode': procode, 'laiyuan': laiyuan}, ensure_ascii=False)

        elif len(tds) == 2:
            info=None




        name = dl.find('a').get_text().strip()
        href = dl.find('a')['href'].strip('../gcxx/')
        ggstart_time = tds[-1].get_text().strip()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.bcactc.com/home/gcxx/' + href
        tmp = [name, ggstart_time, href,info]

        data.append(tmp)
    df = pd.DataFrame(data=data)

    driver.switch_to.parent_frame()
    return df


def f2(driver):
    locator = (By.XPATH, '//iframe[@id="main"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    driver.switch_to.frame('main')

    locator = (By.XPATH, '//table[@id="MyGridView1"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total=driver.find_element_by_xpath('//div[@class="gridview_PagerRow"]/div').text
    total=re.findall('页码：\d/(\d+)',total)[0]

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//table[@class="ContextTable"][string-length()>50]')
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
    div = soup.find('table', class_='ContextTable')

    return div



def get_data():
    data = []

    ggtype2 = OrderedDict([("勘察设计","kc"),("施工", "sg"),("监理", "jl"),("专业", "zy"),
                           ("材料设备","clsb"),("铁路", "td"),("园林", "yl"),("民航", "mh"),
                           ("军队","jd"),("其他", "qt"),])

    ggtype3 = OrderedDict([("勘察设计", "kc_gs"), ("施工", "sg_gs"), ("监理", "jl_gs"), ("专业", "zy_gs"),
                           ("材料设备", "clsb_gs"),("劳务","lw"), ("铁路", "td_gs"), ("园林", "yl_gs"), ("民航", "mh_gs"),
                           ("军队", "jd_gs"), ("其他", "qt_gs"), ])

    ggtype4 = OrderedDict([ ("施工", "sg_zbjg"), ("监理", "jl_zbjg"), ("专业", "zy_zbjg"),
                           ("材料设备", "clsb_zbjg"), ("铁路", "tl_zbjg"), ("园林", "yl_zbjg"),
                           ("军队", "jd_zbjg")])

    for w2 in ggtype2.keys():
        href = "http://www.bcactc.com/home/gcxx/index.aspx?gg&{gc}".format(gc=ggtype2[w2])
        tmp = ["gcjs_zhaobiao_%s_gg" % ( ggtype2[w2]), href, ["name","ggstart_time","href",'info'],
               add_info(f1, {"gclx": w2}), f2]
        data.append(tmp)

    for w2 in ggtype3.keys():
        href = "http://www.bcactc.com/home/gcxx/index.aspx?gs&{gc}".format(gc=ggtype3[w2])
        tmp = ["gcjs_zhongbiaohx_%s_gg" % ( ggtype3[w2]), href, ["name","ggstart_time","href",'info'],
               add_info(f1, {"gclx": w2}), f2]
        data.append(tmp)


    for w2 in ggtype4.keys():
        href = "http://www.bcactc.com/home/gcxx/index.aspx?zbjg&{gc}".format(gc=ggtype4[w2])
        tmp = ["gcjs_zhongbiao_%s_gg" % ( ggtype4[w2]), href, ["name","ggstart_time","href",'info'],
               add_info(f1, {"gclx": w2}), f2]
        data.append(tmp)


    data1 = data.copy()

    return data1


data=get_data()
# pprint(data)



def work(conp, **args):
    est_meta(conp, data=data, diqu="北京市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(
        conp=[
            "postgres",
            "since2015",
            '192.168.3.171',
            "zhixiashi",
            "beijing"],
        headless=True,
        num=1,
        )
    pass