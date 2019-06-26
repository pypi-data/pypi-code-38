from os.path import dirname, join
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
from zhulong.util.etl import gg_meta,gg_html
from zhulong.util.conf import get_conp
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs,gg_existed


_name_="jinhua"



def f1(driver, num):
    locator = (By.XPATH, "(//div[@class='Right-Border floatL']/dl/dt/a)[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//div[@class='Page-bg floatL']/div")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall(r'(\d+)/', st)[0]
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("(//div[@class='Right-Border floatL']/dl/dt/a)[1]").get_attribute('href')[-15:]
        if "http://www.jhztb.gov.cn/platform/project/notice" in url:
            if "type" in url:
                s = "page=%d" % (num-1) if num > 1 else "page=0"
                url = re.sub("type=.*", s, url)
            elif num == 1:
                url = re.sub("page=[0-9]*", "page=0", url)
            else:
                s = "page=%d" % (num-1) if num > 1 else "page=0"
                url = re.sub("page=[0-9]*", s, url)
            driver.get(url)
            locator = (By.XPATH, "(//div[@class='Right-Border floatL']/dl/dt/a)[1][not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        else:
            if "index.htm" in url:
                s = "index_%d" % (num) if num > 1 else "index_1"
                url = re.sub("index", s, url)
            elif num == 1:
                url = re.sub("index_[0-9]*", "index_1", url)
            else:
                s = "index_%d" % (num) if num > 1 else "index_1"
                url = re.sub("index_[0-9]*", s, url)
            driver.get(url)
            locator = (By.XPATH, "(//div[@class='Right-Border floatL']/dl/dt/a)[1][not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("div", class_='Right-Border floatL')
    trs = table.find_all("dt")
    data = []
    for tr in trs:
        info = {}
        a = tr.find("a")
        if re.findall(r'<!--\[(\w+?)\]-->', str(a)):
            diqu = re.findall(r'<!--\[(\w+?)\]-->', str(a))[0]
            info['diqu']= diqu
        if re.findall(r'<!-- <label>【(\w+?)】</label>-->', str(a)):
            zblx = re.findall(r'<!-- <label>【(\w+?)】</label>-->', str(a))[0]
            info['gclx']= zblx
        if a.find('label'):
            zblx = a.find_all('label')[-1].extract().text.strip()
            if re.findall(r'(\w+)',zblx):
                zblx = re.findall(r'(\w+)',zblx)[0]
                info['zbfs'] = zblx
                if a.find('label'):
                    a.find('label').extract()
        try:
            title = a["title"].strip()
        except:
            title = a.text.strip()
        if re.findall(r'^\[(\w+)\]', title):
            diqu = re.findall(r'^\[(\w+)\]', title)[0]
            info['diqu'] = diqu
        link = a["href"]
        td = tr.find("span").text.strip()
        span = re.findall(r'\[(.*)\]', td)[0]
        if "http://www.jhztb.gov.cn/platform/project/notice" in url:
            if re.findall(r'\[(\w+)\]', str(tr)):
                diqu = re.findall(r'\[(\w+)\]', str(tr))[0]
                info['diqu'] = diqu
            link = "http://www.jhztb.gov.cn/platform/project/notice/" + link.strip()
        else:
            link = "http://www.jhztb.gov.cn" + link.strip()
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:
            info = None
        tmp = [title, span, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df



def f2(driver):
    locator = (By.XPATH, "(//div[@class='Right-Border floatL']/dl/dt/a)[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//div[@class='Page-bg floatL']/div")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    num = re.findall(r'/(\d+)', st)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    if "系统发生内部错误" in driver.page_source:
        return 404
    locator = (By.XPATH, "//div[@class='content-Border floatL'][string-length()>30]")
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
    div = soup.find('div', class_='content-Border floatL')
    return div


data = [
    ["gcjs_gqita_yuzhaobiao_shengji_gg",
     "http://www.jhztb.gov.cn/jhztb/szdzbygs/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'省级重点工程', 'gglx':'招标文件公示'}), f2],

    ["gcjs_zhaobiao_shengji_gg",
     "http://www.jhztb.gov.cn/jhztb/gcjyysgs/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'省级重点工程'}),f2],

    ["gcjs_gqita_bian_bu_shengji_gg",
     "http://www.jhztb.gov.cn/jhztb/gcjyzbgg/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'省级重点工程'}), f2],

    ["gcjs_zhongbiaohx_shengji_gg",
     "http://www.jhztb.gov.cn/jhztb/gcjyzbjg/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'省级重点工程'}),f2],

    ["gcjs_zhongbiao_shengji_gg",
     "http://www.jhztb.gov.cn/jhztb/gcjyzbzy/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'省级重点工程'}), f2],
    #
    ["gcjs_zhaobiao_shiji_gg",
     "http://www.jhztb.gov.cn/jhztb/jsgcgcjszbgg/index.htm",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'市本级工程'}),f2],

    ["gcjs_gqita_bian_bu_shiji_gg",
     "http://www.jhztb.gov.cn/jhztb/jsgcgcjsdycq/index.htm",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'市本级工程'}), f2],

    ["gcjs_zhongbiaohx_shiji_gg",
     "http://www.jhztb.gov.cn/jhztb/jsgcgcjspbjg/index.htm",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'市本级工程'}), f2],

    ["gcjs_zhongbiao_shiji_gg",
     "http://www.jhztb.gov.cn/jhztb/jsgcgcjszbjg/index.htm",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'市本级工程'}), f2],
    #
    ["gcjs_zhaobiao_jhs_gg",
     "http://www.jhztb.gov.cn/jhztb/jsgcjhszbgg/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'金华山工程'}), f2],

    ["gcjs_gqita_bian_bu_jhs_gg",
     "http://www.jhztb.gov.cn/jhztb/jsgcjhsdycq/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'金华山工程'}), f2],

    ["gcjs_zhongbiaohx_jhs_gg",
     "http://www.jhztb.gov.cn/jhztb/jsgcjhspbjg/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'金华山工程'}), f2],

    ["gcjs_zhongbiao_jhs_gg",
     "http://www.jhztb.gov.cn/jhztb/jsgcjhszbjg/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'金华山工程'}), f2],
    #
    ["zfcg_yucai_gg",
     "http://www.jhztb.gov.cn/jhztb/zfcgggyg/index.htm",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhaobiao_gg",
     "http://www.jhztb.gov.cn/jhztb/zfcgcggg/index.htm",
     ["name", "ggstart_time", "href", "info"],f1,f2],
    #
    ["zfcg_gqita_zhonghx_liu_gg",
     "http://www.jhztb.gov.cn/jhztb/zfcgzbgg/index.htm",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhongbiao_gg",
     "http://www.jhztb.gov.cn/jhztb/zfcgzbhxgs/index.htm",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhaobiao_shixian_gg",
     "http://www.jhztb.gov.cn/platform/project/notice/list.jsp?key=tenderBulletin&area=&type=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'金华各县(市)分中心交易信息'}), f2],

    ["gcjs_kaibiao_shixian_gg",
     "http://www.jhztb.gov.cn/platform/project/notice/list.jsp?key=openBidRecord&area=&type=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'金华各县(市)分中心交易信息'}), f2],

    ["gcjs_zhongbiao_shixian_gg",
     "http://www.jhztb.gov.cn/platform/project/notice/list.jsp?key=winBidBulletin&area=&type=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'金华各县(市)分中心交易信息'}), f2],

    ["gcjs_zhongbiaohx_shixian_gg",
     "http://www.jhztb.gov.cn/platform/project/notice/list.jsp?key=winCandidateBulletin&area=&type=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'金华各县(市)分中心交易信息'}), f2],

    ["gcjs_zgys_shixian_gg",
     "http://www.jhztb.gov.cn/platform/project/notice/list.jsp?key=qualifyBulletin&area=&type=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'金华各县(市)分中心交易信息'}), f2],

    ["zfcg_zhaobiao_shixian_gg",
     "http://www.jhztb.gov.cn/platform/project/notice/list.jsp?key=caiGouGGZFCG&area=&type=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'金华各县(市)分中心交易信息'}), f2],

    ["zfcg_zhongbiao_shixian_gg",
     "http://www.jhztb.gov.cn/platform/project/notice/list.jsp?key=zhongBiaoResultZFCG&area=&type=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'金华各县(市)分中心交易信息'}), f2],

    ["qsy_zhaobiao_shixian_gg",
     "http://www.jhztb.gov.cn/platform/project/notice/list.jsp?key=OTHER_TRADE_PUB_INFO&area=&type=5",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'金华各县(市)分中心交易信息','gglx':'其他交易'}), f2],

    ["qsy_zhongbiao_shixian_gg",
     "http://www.jhztb.gov.cn/platform/project/notice/list.jsp?key=OTHER_TRADE_RESULT_INFO&area=&type=5",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'金华各县(市)分中心交易信息','gglx':'其他交易'}), f2],
]



def work(conp,**args):
    est_meta(conp,data=data,diqu="浙江省金华市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","zhejiang","jinhua"],pageloadtimeout=120)



