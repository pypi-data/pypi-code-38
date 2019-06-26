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


_name_="huzhou"


def f1(driver, num):
    locator = (By.XPATH, "(//a[@class='WebList_sub'])[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//td[@class='huifont']")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall(r'(\d+)/', st)[0]

    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("(//a[@class='WebList_sub'])[1]").get_attribute('href')[-40:]
        if num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
        driver.get(url)
        locator = (By.XPATH, "(//a[@class='WebList_sub'])[1][not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", width='98%')
    trs = table.find_all("tr", height="24")
    data = []
    for tr in trs[1:]:
        info = {}
        a = tr.find("a")
        if a.find('font'):
            diqu = a.find('font').extract().text.strip()
            if re.findall(r'\[(.*)\]', diqu):
                diqu = re.findall(r'\[(.*)\]', diqu)[0]
            info['diqu'] = diqu
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        link = a["href"]
        if 'http' in link:
            href = link.strip()
        else:
            href = "http://ggzy.huzhou.gov.cn" + link.strip()
        td = tr.find("td", width="80").text.strip()
        if re.findall(r'^【(.*?)】', title):
            gglx = re.findall(r'^【(.*?)】', title)[0]
            info['gglx'] = gglx
        if re.findall(r'^\[(.*?)\]', title):
            lx = re.findall(r'^\[(.*?)\]', title)[0]
            info['lx'] = lx
        if info:info = json.dumps(info, ensure_ascii=False)
        else:info = None
        tmp = [title, td, href, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.XPATH, "(//a[@class='WebList_sub'])[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, '//td[@class="huifont"]')
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    num = re.findall(r'/(\d+)', st)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//td[@height='859'][string-length()>40]")
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
    div = soup.find('td', height='859')
    return div


data = [
    ["gcjs_zhaobiao_jianshe_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jyxx_HuZhou/029001/029001001/029001001001/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'gclx':'建设'}),f2],

    ["gcjs_zhongbiao_jianshe_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jyxx_HuZhou/029001/029001001/029001001002/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'gclx':'建设'}),f2],

    ["gcjs_zhaobiao_jiaotong_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jyxx_HuZhou/029001/029001002/029001002001/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'gclx':'交通'}),f2],

    ["gcjs_zhongbiao_jiaotong_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jyxx_HuZhou/029001/029001002/029001002002/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'gclx':'交通'}),f2],


    ["gcjs_zhaobiao_shuili_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jyxx_HuZhou/029001/029001003/029001003001/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'gclx':'水利'}),f2],

    ["gcjs_zhongbiao_shuli_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jyxx_HuZhou/029001/029001003/029001003002/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'gclx':'水利'}),f2],

    ["gcjs_zhaobiao_xianer_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jyxx_HuZhou/029001/029001004/029001004001/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'gclx':'限额以下'}),f2],


    ["zfcg_zhaobiao_jizhong_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jyxx_HuZhou/029004/029004001/029004001001/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs':'集中采购'}),f2],

    ["zfcg_gqita_zhong_liu_jizhong_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jyxx_HuZhou/029004/029004001/029004001002/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs':'集中采购'}),f2],

    ["zfcg_yucai_jizhong_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jyxx_HuZhou/029004/029004001/029004001003/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs':'集中采购'}),f2],


    ["zfcg_zhaobiao_fensan_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jyxx_HuZhou/029004/029004002/029004002001/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs':'分散采购'}),f2],

    ["zfcg_zhongbiao_fensan_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jyxx_HuZhou/029004/029004002/029004002002/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs':'分散采购'}),f2],

    ["zfcg_yucai_fensan_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jyxx_HuZhou/029004/029004002/029004002003/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs':'分散采购'}),f2],

    ["zfcg_gqita_caigoumulu_jizhong_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jyxx_HuZhou/029004/029004005/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs':'集中采购','jylx':'集中采购目录'}),f2],

    ["yiliao_zhaobiao_jizhong_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jyxx_HuZhou/029005/029005001/029005001001/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs':'集中采购'}),f2],

    ["yiliao_zhongbiao_jizhong_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jyxx_HuZhou/029005/029005001/029005001002/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs':'集中采购'}),f2],

    ["yiliao_zhaobiao_fensan_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jyxx_HuZhou/029005/029005002/029005002001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'分散采购'}), f2],

    ["yiliao_zhongbiao_fensan_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jyxx_HuZhou/029005/029005002/029005002002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'分散采购'}), f2],
]


def work(conp,**args):
    est_meta(conp,data=data,diqu="浙江省湖州市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","zhejiang","huzhou"])
