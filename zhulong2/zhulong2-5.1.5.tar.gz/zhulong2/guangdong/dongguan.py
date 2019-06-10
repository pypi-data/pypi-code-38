import os
import random

import cv2
import pandas as pd
import re

import requests
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

import time

from sklearn.externals import joblib
from zhulong2.util.etl import est_html, est_meta, add_info

_name_ = "guangdong_dongguan"


t_num = 0
list1 = []
def save_yzm_img(driver, num):
    img = driver.find_element_by_xpath('//img[@class="yzmimg y"]')
    driver.maximize_window()
    driver.save_screenshot("full_snap%s.png" % num)
    location = img.location
    size = img.size
    # 无头模式减417.有头不用
    left = location['x'] - 417

    top = location['y']
    right = left + size['width']
    bottom = top + size['height']  # img4[y:y + h, x:x + w]
    # page_snap_obj = Image.open("full_snap%s.png"%num)
    page_snap_obj1 = cv2.imread("full_snap%s.png" % num)[top:top + bottom, left:left + right]
    os.remove('full_snap%s.png' % num)
    # cv2.imwrite('1.png',page_snap_obj1)
    # image_obj = page_snap_obj.crop((left, top, right, bottom))
    # image_obj.save("yzm"+str(num)+".png")
    # yzm_img = cv2.imread("yzm"+str(num)+".png")
    return page_snap_obj1


def parse_img(img):
    '''图像'''
    global t_num,list1
    img2 = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    ret, img3 = cv2.threshold(img2, 127, 255, cv2.THRESH_BINARY)
    img4 = cv2.medianBlur(img3, 1)
    contours, hierarchy = cv2.findContours(img4, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # 查找文件的绝对路径
    if t_num < 1:
        ss = os.popen('find / -name yzm_model.m', mode="r", buffering=-1)
        s = ss.read()
        list2 = s.split('\n')
        for li in list2:
            if '/zhulong2/guangdong/yzm_model.m' in li:
                list1.append(li)
                t_num += 1
    if list1:
        clf = joblib.load(list1[0])
    else:
        clf = joblib.load('yzm_model.m')
    text = []
    for i, cnt in enumerate(contours):
        x, y, w, h = cv2.boundingRect(cnt)
        if x != 0 and y != 0 and w * h >= 100:
            im = cv2.resize(img4[y:y + h, x:x + w], (64, 48)).reshape(-1) / 255
            t = clf.predict([im])
            text.append(t[0])

    text.reverse()
    return ''.join(text)


def f1(driver, num):
    url = driver.current_url
    locator = (By.XPATH, "//tbody[@class='tableBody']/tr[1]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//select[@name='__ec_pages']/option[@selected='selected']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(st)
    except:
        cnum = 1

    if num != cnum:
        val = driver.find_element_by_xpath("//tbody[@class='tableBody']/tr[1]/td/a").get_attribute('href')[-12:]

        selector = Select(driver.find_element_by_xpath("//select[@name='__ec_pages']"))
        selector.select_by_value('{}'.format(num))
        flag = 0
        while "请输入验证码" in driver.page_source:
            driver.execute_script('window.scrollTo(500,0)')

            img = save_yzm_img(driver, num)
            text = parse_img(img)
            driver.find_element_by_xpath('//input[@id="verify"]').send_keys(text)
            driver.find_element_by_xpath('//input[@class="yzmbox_submit roundimgx"]').click()
            flag += 1
            if flag >= 15:
                break

        locator = (By.XPATH, "//tbody[@class='tableBody']/tr[1]/td/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("tbody", class_="tableBody")
    trs = div.find_all("tr")
    data = []
    for tr in trs:
        a = tr.find('a')
        title = a.text.strip()
        td = tr.find_all('td')[-1].text.strip()
        href = a['href'].strip()
        id = re.findall(r'id=(.*)', href)[0]
        link = 'http://czj.dg.gov.cn/dggp/portal/documentView.do?method=view&id=' + id
        tmp = [title, td, link]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//tbody[@class='tableBody']/tr[1]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//select[@name='__ec_pages']/option[last()]")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        page_all = int(str)
    except:
        page_all = 1
    driver.quit()
    return page_all


def f3(driver, url):
    driver.get(url)
    try:
        locator = (By.XPATH,
                   "//div[@class='container'][string-length()>10] | //tbody[@id='templateBody'][string-length()>10] | //table[@width='93%'][string-length()>10] | //table[@cellspacing='1'][string-length()>10]　|　//div[@class='xl-right'][string-length()>10]")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    except:
        flag = 0
        num = url[-10:]
        while "请输入验证码" in driver.page_source:
            time.sleep(1)
            num += '1'
            driver.execute_script('window.scrollTo(500,0)')
            img = save_yzm_img(driver, num)
            text = parse_img(img)
            # os.remove("yzm"+str(num)+".png")
            # print(text)
            driver.find_element_by_xpath('//input[@id="verify"]').send_keys(text)
            driver.find_element_by_xpath('//input[@class="yzmbox_submit roundimgx"]').click()
            flag += 1
            if flag >= 15:
                break
        locator = (By.XPATH,
                   "//tbody[@id='templateBody'][string-length()>10] | //table[@width='93%'][string-length()>10] | //table[@cellspacing='1'][string-length()>10]　|　//div[@class='xl-right'][string-length()>10]")
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
    div = soup.find('tbody', id='templateBody')
    if div == None:
        div = soup.find('table', attrs={'width': '93%'})
        if div == None:
            div = soup.find('table', attrs={'cellspacing': '1'})
            if div == None:
                div = soup.find('div', class_='xl-right')
                if div == None:
                    div = soup.find('div', class_='container')
    # div=div.find_all('div',class_='ewb-article')[0]

    return div


data = [
    ["zfcg_gqita_zhao_liu_wsjj_gg", "http://czj.dg.gov.cn/dggp/portal/topicView.do?method=view&id=80808",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '网上竞价'}), f2],
    # #
    ["zfcg_gqita_cgjh_shiji_gg", "http://czj.dg.gov.cn/dggp/portal/topicView.do?method=view&id=8034944",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '采购计划公告', 'diqu': '市级'}), f2],
    # #
    ["zfcg_yucai_shiji_gg", "http://czj.dg.gov.cn/dggp/portal/topicView.do?method=view&id=16519200",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '采购计划公告', 'diqu': '市级'}), f2],
    #
    ["zfcg_zhaobiao_shiji_gg", "http://czj.dg.gov.cn/dggp/portal/topicView.do?method=view&id=1660",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],
    #
    ["zfcg_biangeng_shiji_gg", "http://czj.dg.gov.cn/dggp/portal/topicView.do?method=view&id=1663",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],
    #
    ["zfcg_gqita_zhonghx_zsjg_shiji_gg", "http://czj.dg.gov.cn/dggp/portal/topicView.do?method=view&id=904469593",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],
    #
    ["zfcg_zhongbiao_shiji_gg", "http://czj.dg.gov.cn/dggp/portal/topicView.do?method=view&id=2014",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],
    #
    ["zfcg_zhongbiao_plcg_shiji_gg", "http://czj.dg.gov.cn/dggp/portal/topicView.do?method=view&id=976401",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'zbfs': '集中采购'}), f2],
    #
    ["zfcg_hetong_shiji_gg", "http://czj.dg.gov.cn/dggp/portal/topicView.do?method=view&id=51536459",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],
    # #
    ["zfcg_gqita_cgjh_zhenjie_gg", "http://czj.dg.gov.cn/dggp/portal/topicView.do?method=view&id=8034945",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '采购计划公告', 'diqu': '镇街'}), f2],
    # #
    ["zfcg_zhaobiao_zhenjie_gg", "http://czj.dg.gov.cn/dggp/portal/topicView.do?method=view&id=1662",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '镇街'}), f2],
    # #
    ["zfcg_biangeng_zhenjie_gg", "http://czj.dg.gov.cn/dggp/portal/topicView.do?method=view&id=51530072",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '镇街'}), f2],
    # #
    ["zfcg_zhongbiao_zhenjie_gg", "http://czj.dg.gov.cn/dggp/portal/topicView.do?method=view&id=51530002",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '镇街'}), f2],
    # #
    ["zfcg_hetong_zhenjie_gg", "http://czj.dg.gov.cn/dggp/portal/topicView.do?method=view&id=51538122",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '镇街'}), f2],
    # #
    ["zfcg_zhaobiao_jinkou_gg",
     "http://czj.dg.gov.cn/dggp/portal/topicView.do?method=specialTopIdView&specialTopId=allBulletinsImport",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '审核前公示', 'zbfs': '进口产品'}), f2],
    #
    ["zfcg_zhaobiao_danyilaiyuan_gg",
     "http://czj.dg.gov.cn/dggp/portal/topicView.do?method=specialTopIdView&specialTopId=allUnaudit60",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '审核前公示', 'zbfs': '单一来源'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省东莞市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "dongguan"])


    # driver=webdriver.Chrome()
    # url = "http://czj.dg.gov.cn/dggp/portal/topicView.do?method=view&id=8034944"
    # driver.get(url)
    # d = f3(driver, 'http://czj.dg.gov.cn/dggp/portal/documentView.do?method=view&id=2544964')
    # print(d)
    # df = f2(driver)
    # print(df)
    # cp = webdriver.ChromeOptions()
    # cp.add_argument('--headless')
    # driver= webdriver.Chrome(chrome_options=cp)
    # url = "http://czj.dg.gov.cn/dggp/portal/topicView.do?method=view&id=8034944"
    # driver.get(url)
    # for i in range(13, 25):
    #     df=f1(driver, i)
    #     print(df.values)
