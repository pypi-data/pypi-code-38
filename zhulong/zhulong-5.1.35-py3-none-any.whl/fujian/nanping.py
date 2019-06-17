
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
from zhulong.util.etl import add_info, est_meta, est_html, est_tbs, gg_existed

_name_="nanping"


def zfcg_data(driver, num):
    url = driver.current_url
    locator = (By.XPATH, "//table[@class='table table-hover dataTables-example']/tbody/tr[1]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//button[@class='active']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        cnum = int(st)
    except:
        cnum = 1
    try:
        notice_type = re.findall(r'notice_type=(.*)&', url)[0]
    except:
        notice_type = re.findall(r'notice_type=(.*)', url)[0]

    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@class='table table-hover dataTables-example']/tbody/tr[1]/td/a").get_attribute('href')[-30:]
        driver.execute_script("javascript:location.href='?page={0}&notice_type={1}'".format(num, notice_type))
        # driver.execute_script("javascript:location.href='?page=6&notice_type=7dc00df822464bedbf9e59d02702b714'")
        try:
            locator = (By.XPATH,
                       "//table[@class='table table-hover dataTables-example']/tbody/tr[1]/td/a[not(contains(@href,'%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            driver.refresh()
            locator = (By.XPATH,
                       "//table[@class='table table-hover dataTables-example']/tbody/tr[1]/td/a[not(contains(@href,'%s'))]" % val)
            WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", class_="table table-hover dataTables-example")
    tbody = table.find('tbody')

    trs = tbody.find_all("tr", class_="gradeX")
    data = []
    for tr in trs:
        a = tr.find('a')
        try:
            title = a["title"].strip()
        except:
            title = a.text.strip()
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = "http://np.fjzfcg.gov.cn:8090" + link.strip()
        td = tr.find_all("td")[4].text.strip()
        diqu = tr.find_all("td")[0].text.strip()
        cgfs = tr.find_all("td")[1].text.strip()
        cgdw = tr.find_all("td")[2].text.strip()
        dd = {'diqu': diqu, 'cgfs': cgfs, 'cgdw': cgdw}
        info = json.dumps(dd, ensure_ascii=False)
        tmp = [title, td, href, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f1(driver, num):
    url = driver.current_url
    if "http://np.fjzfcg.gov.cn" in url:
        df = zfcg_data(driver, num)
        return df
    elif "/jsgc/" in url:
        locator = (By.XPATH, "//tr[@class='trfont'][1]/td/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "//td[@class='huifont']")
            st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            cnum = re.findall(r'(\d+)/', st)[0]
        except:
            cnum = 1
        if num != int(cnum):
            val = driver.find_element_by_xpath("//tr[@class='trfont'][1]/td/a").get_attribute('href')[-30:]
            if "Paging" not in url:
                s = "?Paging=%d" % (num) if num > 1 else "?Paging=1"
                url = url + s
            elif num == 1:
                url = re.sub("Paging=[0-9]*", "Paging=1", url)
            else:
                s = "Paging=%d" % (num) if num > 1 else "Paging=1"
                url = re.sub("Paging=[0-9]*", s, url)
            driver.get(url)
            locator = (By.XPATH, "//tr[@class='trfont'][1]/td/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        table = soup.find("table", cellspacing="3")
        trs = table.find_all("tr", class_='trfont')
        data = []
        for tr in trs:
            a = tr.find('a')
            try:
                title = a["title"].strip()
            except:
                title = a.text.strip()
            link = a["href"]
            if 'http' in link:
                href = link
            else:
                href = "http://ggzy.np.gov.cn" + link.strip()
            td = tr.find("td", align="right").text.strip()
            td = re.findall(r'\[(.*)\]', td)[0]
            tmp = [title, td, href]
            data.append(tmp)
        df = pd.DataFrame(data)
        df['info'] = None
        return df
    else:
        locator = (By.XPATH, "//li[@class='content-item'][1]/a")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-30:]
        try:
            locator = (By.XPATH, "//a[@class='wb-page-default wb-page-number wb-page-family']")
            st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            cnum = re.findall(r'(\d+)/', st)[0]
        except:
            cnum = 1
        if num != int(cnum):
            driver.find_element_by_xpath('//input[@id="GoToPagingNo"]').clear()
            driver.find_element_by_xpath('//input[@id="GoToPagingNo"]').send_keys(num)
            driver.find_element_by_xpath('//a[@class="wb-page-item wb-page-next wb-page-go wb-page-fs12"]').click()
            locator = (By.XPATH, "//li[@class='content-item'][1]/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        table = soup.find("ul", class_="content-list clearfix")
        trs = table.find_all("li", class_='content-item')
        data = []
        for tr in trs:
            a = tr.find('a')
            try:
                title = tr.find('span', class_='link-content').text.strip()
            except:
                title = a.text.strip()
            link = a["href"]
            if 'http' in link:
                href = link
            else:
                href = "http://ggzy.np.gov.cn" + link.strip()
            td = tr.find("span", class_="time").text.strip()
            tmp = [title, td, href]
            data.append(tmp)
        df = pd.DataFrame(data)
        df['info'] = None
        return df



def f2(driver):
    url = driver.current_url
    if ('本栏目暂无信息' in driver.page_source) or ('暂无数据' in driver.page_source):
        return 0
    elif "http://np.fjzfcg.gov.cn" in url:
        locator = (By.XPATH, "//button[@class='active']")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        locator = (By.XPATH, "//div[@class='pageGroup']/button[last()]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        try:
            locator = (By.XPATH, "//button[@class='active'][not(contains(string(),'%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            locator = (By.XPATH, "//button[@class='active']")
            str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num = int(str)
        except:
            num = 1
        driver.quit()
        return int(num)
    elif "/jsgc/" in url:
        locator = (By.XPATH, "//tr[@class='trfont'][1]/td/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "//td[@class='huifont']")
            str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num = re.findall(r'/(\d+)', str)[0]
        except:
            num = 1
        driver.quit()
        return int(num)
    else:
        locator = (By.XPATH, "//li[@class='content-item'][1]/a/span[1]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "//a[@class='wb-page-default wb-page-number wb-page-family']")
            str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num = re.findall(r'/(\d+)', str)[0]
        except:
            num = 1
        driver.quit()
        return int(num)



def f3(driver, url):
    driver.get(url)
    if ('无法访问此网站' in driver.page_source) or ('404' in driver.title):
        return 404
    elif "http://np.fjzfcg.gov.cn" in url:
        locator = (By.XPATH, "//div[@id='print-content'][string-length()>30]")
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
        div = soup.find('div', id="print-content")
        # div=div.find_all('div',class_='ewb-article')[0]
        return div
    elif "categoryNum=01000" in url:
        categoryNum = int(url[-1])
        locator = (By.XPATH, "//div[@id='menutab_6_{}'][string-length()>30]".format(categoryNum))
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
        div = soup.find('div', id="menutab_6_{}".format(categoryNum))
        div = div.find('td', style="line-height: 25px; color: #4e4e4e; text-align:left;")
        return div
    else:
        locator = (By.XPATH, "//div[@class='article-block'][string-length()>30]")
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
        div = soup.find('div', class_="article-block")
        return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://ggzy.np.gov.cn/npztb/jsgc/010001/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://ggzy.np.gov.cn/npztb/jsgc/010002/",
     ["name", "ggstart_time", "href", "info"],f1, f2],

    ["gcjs_gqita_zhonghx_liu_gg",
     "http://ggzy.np.gov.cn/npztb/jsgc/010004/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiao_gg",
     "http://ggzy.np.gov.cn/npztb/jsgc/010005/",
     ["name", "ggstart_time", "href", "info"],f1, f2],

    ["zfcg_zhaobiao_jizhong_gg",
     "http://ggzy.np.gov.cn/npztb/zfjzcg/009001/",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_gqita_zhao_liu_jizhong_gg",
     "http://ggzy.np.gov.cn/npztb/zfjzcg/009003/",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_biangeng_jizhong_gg",
     "http://ggzy.np.gov.cn/npztb/zfjzcg/009004/",
     ["name", "ggstart_time", "href", "info"],f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://np.fjzfcg.gov.cn:8090/350700/noticelist/d03180adb4de41acbb063875889f9af1/?zone_code=350700&zone_name=%E5%8D%97%E5%B9%B3%E5%B8%82&croporgan_name=&project_no=&fromtime=&endtime=&gpmethod=&agency_name=&title=&notice_type=463fa57862ea4cc79232158f5ed02d03&purchase_item_name=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://np.fjzfcg.gov.cn:8090/350700/noticelist/d03180adb4de41acbb063875889f9af1/?zone_code=350700&zone_name=%E5%8D%97%E5%B9%B3%E5%B8%82&croporgan_name=&project_no=&fromtime=&endtime=&gpmethod=&agency_name=&title=&notice_type=7dc00df822464bedbf9e59d02702b714&purchase_item_name=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://np.fjzfcg.gov.cn:8090/350700/noticelist/d03180adb4de41acbb063875889f9af1/?zone_code=350700&zone_name=%E5%8D%97%E5%B9%B3%E5%B8%82&croporgan_name=&project_no=&fromtime=&endtime=&gpmethod=&agency_name=&title=&notice_type=b716da75fe8d4e4387f5a8c72ac2a937&purchase_item_name=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_jieguo_gg",
     "http://np.fjzfcg.gov.cn:8090/350700/noticelist/d03180adb4de41acbb063875889f9af1/?zone_code=350700&zone_name=%E5%8D%97%E5%B9%B3%E5%B8%82&croporgan_name=&project_no=&fromtime=&endtime=&gpmethod=&agency_name=&title=&notice_type=d812e46569204c7fbd24cbe9866d0651&purchase_item_name=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_danyilaiyuan_gg",
     "http://np.fjzfcg.gov.cn:8090/350700/noticelist/d03180adb4de41acbb063875889f9af1/?zone_code=350700&zone_name=%E5%8D%97%E5%B9%B3%E5%B8%82&croporgan_name=&project_no=&fromtime=&endtime=&gpmethod=&agency_name=&title=&notice_type=255e087cf55a42139a1f1b176b244ebb&purchase_item_name=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"zbfs":"单一来源"}), f2],

    ["qsy_zhaobiao_gg",
     "http://ggzy.np.gov.cn/npztb/qxzbxx/013001/",
     ["name", "ggstart_time", "href", "info"],f1, f2],

    ["qsy_gqita_bian_bu_gg",
     "http://ggzy.np.gov.cn/npztb/qxzbxx/013002/",
     ["name", "ggstart_time", "href", "info"],f1, f2],

    ["qsy_gqita_zhonghx_liu_gg",
     "http://ggzy.np.gov.cn/npztb/qxzbxx/013004/",
     ["name", "ggstart_time", "href", "info"],f1, f2],

    ["qsy_gqita_zhong_liu_gg",
     "http://ggzy.np.gov.cn/npztb/qxzbxx/013005/",
     ["name", "ggstart_time", "href", "info"],f1, f2],

]





def work(conp,**args):
    est_meta(conp,data=data,diqu="福建省南平市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","fujian","nanping"])


# 修改时间：2019/5/16
# 网址更替：http://ggzy.np.gov.cn/npztb