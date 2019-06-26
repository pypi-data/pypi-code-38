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
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs


_name_="yiwu"



def f1(driver, num):
    locator = (By.XPATH, "//div[@class='ewb-main-bd']/ul/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//span[@id='index']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        cnum = re.findall(r'(\d+)/', str)[0]
    except:
        cnum = 1
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='ewb-main-bd']/ul/li[last()]/a").get_attribute('href')[-30:]
        if ("list3gc.html" in url) or ("list3" in url) or ("list3qt" in url):
            s = "/%d.html" % (num) if num > 1 else "/1.html"
            url = re.sub("/list3gc\.html", s, url)
            url = re.sub("/list3\.html", s, url)
            url = re.sub("/list3qt\.html", s, url)
        elif num == 1:
            url = re.sub("/[0-9]*\.html", "/1.html", url)
        else:
            s = "/%d.html" % (num) if num > 1 else "/1.html"
            url = re.sub("/[0-9]*\.html", s, url)
        driver.get(url)
        try:
            locator = (By.XPATH, "//div[@class='ewb-main-bd']/ul/li[1]/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            driver.refresh()
            locator = (By.XPATH, "//div[@class='ewb-main-bd']/ul/li[1]/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("div", class_='ewb-main-bd').ul
    trs = table.find_all("li")
    data = []
    for tr in trs:
        info = {}
        a = tr.find("a")
        if a.find('span', style="color:#CB31DD"):
            zbfs = a.find('span', style="color:#CB31DD").extract().text.strip()
            if re.findall(r'(\w+)', zbfs):
                zbfs = re.findall(r'(\w+)', zbfs)[0]
                info['zbfs'] = zbfs
        try:
            title = a["title"].strip()
        except:
            title = a.text.strip()
        if re.findall(r'^【(\w+)】', title):
            diqu = re.findall(r'^【(\w+)】', title)[0]
            info['diqu'] = diqu
        td = tr.find("span", class_="ewb-date r").text.strip()
        link = "http://ywjypt.com"+a["href"].strip()
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:
            info = None
        tmp = [title, td, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='ewb-main-bd']/ul/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//span[@id='index']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        num = int(re.findall(r'/(\d+)', str)[0])
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    if '404' in driver.title:
        return 404
    locator = (By.XPATH, "//div[@class='news-article'][string-length()>30]")
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
    div = soup.find('div', attrs={'class':'news-article','style':False})
    return div


data = [
    ["gcjs_gqita_yuzhaobiao_gg",
     "http://ywjypt.com/jyxx/070001/070001015/list3gc.html",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'gglx':'项目基本信息'}),f2],

    ["gcjs_zgys_gg",
     "http://ywjypt.com/jyxx/070001/070001002/list3gc.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_gg",
     "http://ywjypt.com/jyxx/070001/070001001/list3gc.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_biangeng_gg",
     "http://ywjypt.com/jyxx/070001/070001006/list3gc.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_liubiao_gg",
     "http://ywjypt.com/jyxx/070001/070001007/list3gc.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_kaibiao_gg",
     "http://ywjypt.com/jyxx/070001/070001009/list3gc.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiaohx_gg",
     "http://ywjypt.com/jyxx/070001/070001004/list3gc.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_dingbiao_gg",
     "http://ywjypt.com/jyxx/070001/070001008/list3gc.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'定标公示'}), f2],

    ["gcjs_zhongbiao_gg",
     "http://ywjypt.com/jyxx/070001/070001005/list3gc.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_hetong_gg",
     "http://ywjypt.com/jyxx/070001/070001011/list3gc.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_yucai_gg",
     "http://ywjypt.com/jyxx/070002/070002004/list3.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhaobiao_gg",
     "http://ywjypt.com/jyxx/070002/070002001/list3.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://ywjypt.com/jyxx/070002/070002003/list3.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_gqita_zhong_liu_gg",
     "http://ywjypt.com/jyxx/070002/070002002/list3.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_hetong_gg",
     "http://ywjypt.com/jyxx/070002/070002006/list3.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_yanshou_gg",
     "http://ywjypt.com/jyxx/070002/070002008/list3.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["qsy_yucai_gg",
     "http://ywjypt.com/jyxx/070005/070005003/list3.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'国企采购'}), f2],

    ["qsy_zhaobiao_gg",
     "http://ywjypt.com/jyxx/070005/070005001/list3.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'国企采购'}), f2],

    ["qsy_biangeng_gg",
     "http://ywjypt.com/jyxx/070005/070005002/list3.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'国企采购'}), f2],

    ["qsy_zhongbiaohx_gg",
     "http://ywjypt.com/jyxx/070005/070005006/list3.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'国企采购'}), f2],

    ["qsy_gqita_dingbiao_gg",
     "http://ywjypt.com/jyxx/070005/070005010/list3.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'国企采购','gglx':'定标公示'}), f2],

    ["qsy_zhongbiao_gg",
     "http://ywjypt.com/jyxx/070005/070005004/list3.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'国企采购'}), f2],

    ["jqita_zhaobiao_gg",
     "http://ywjypt.com/jyxx/070008/070008001/list3qt.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'其他交易'}), f2],

    ["jqita_biangeng_gg",
     "http://ywjypt.com/jyxx/070008/070008002/list3qt.html",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'其他交易'}), f2],

    ["jqita_zhongbiao_gg",
     "http://ywjypt.com/jyxx/070008/070008003/list3qt.html",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'其他交易'}), f2],

    ["jqita_yucai_xiangzhen_gg",
     "http://ywjypt.com/jyxx/070008/070008007/list3qt.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'其他交易','gglx':'镇采公告'}), f2],

    ["jqita_zhaobiao_xiangzhen_gg",
     "http://ywjypt.com/jyxx/070008/070008004/list3qt.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'其他交易','gglx':'镇采公告'}), f2],

    ["jqita_biangeng_xiangzhen_gg",
     "http://ywjypt.com/jyxx/070008/070008005/list3qt.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'其他交易','gglx':'镇采公告'}), f2],

    ["jqita_zhongbiao_xiangzhen_gg",
     "http://ywjypt.com/jyxx/070008/070008006/list3qt.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'其他交易','gglx':'镇采公告'}), f2],


]


def work(conp,**args):
    est_meta(conp,data=data,diqu="浙江省义乌市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","zhejiang","yiwu"])

