import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_command,db_query
from selenium.webdriver import DesiredCapabilities
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


_name_="yaan"


def f2_data(driver, num):
    locator = (By.XPATH, '//div[@class="new_news_content"]/ul/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//td[@class='page_bar']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = re.findall(r'(\d+)/', st)[0]
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath('//div[@class="new_news_content"]/ul/li[1]//a').get_attribute('href')[-35:]
        locator = (By.XPATH, '//*[@id="txtAjax_PageIndex"]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).clear()
        locator = (By.XPATH, '//*[@id="txtAjax_PageIndex"]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).send_keys(num)
        locator = (By.XPATH, '//*[@id="tbPager"]/tbody/tr/td[1]/span[3]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()

        locator = (By.XPATH, "//div[@class='new_news_content']/ul/li[1]//a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("div", class_="new_news_content")
    trs = table.find_all("li")
    data = []
    for tr in trs:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        href = a['href'].strip()
        if "http" in href:
            link = href
        else:
            link = "http://www.yaggzy.org.cn" + a['href'].strip()
        try:
            span = tr.find('span', class_="time")
            if span == None:span = tr.find('span', class_="tiam")
            span = span.text.strip()
        except:
            span = '-'
        info = {}
        if re.findall(r'^\[(.*?)\]', title):
            tds = re.findall(r'^\[(.*?)\]', title)[0]
            info['diqu'] = tds
        if tr.find('span', attrs={'class':'carmore','style':'width: 75px!important;'}):
            lx = tr.find('span', attrs={'class':'carmore','style':'width: 75px!important;'}).text.strip()
            info['lx'] = lx
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:
            info = None
        tmp = [title, span, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df




def f1(driver, num):
    url = driver.current_url
    if '/zfcgwsjjpt/JyWeb/' in url:
        df = f2_data(driver, num)
        return df
    locator = (By.XPATH, "//li[@class='clearfloat']/table/tbody/tr[2]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//a[@class='cur']")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    if num != int(cnum):
        val = driver.find_element_by_xpath("//li[@class='clearfloat']/table/tbody/tr[2]/td/a").get_attribute('href')[-35:]
        driver.execute_script('pagination({});return false;'.format(num))
        locator = (By.XPATH, "//li[@class='clearfloat']/table/tbody/tr[2]/td/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("li", class_='clearfloat')
    table = table.find('table')
    trs = table.find_all("tr")
    data = []
    for tr in trs[1:]:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        link = "http://www.yaggzy.org.cn" + a['href'].strip()

        if '/jyxx/jsgcLbgs' in url:
            td = tr.find_all("td")[-1].text.strip()
            info = {}
            if tr.find_all("td")[-2]:
                state = tr.find_all("td")[-2].text.strip()
                info['state'] =state
            if tr.find_all("td")[-3]:
                kb_time = tr.find_all("td")[-3].text.strip()
                info['kb_time'] = kb_time
            if info:
                info = json.dumps(info, ensure_ascii=False)
            else:
                info = None
        else:
            tds = tr.find_all("td")[-1].text.strip()
            if tds == '--':
                continue
            try:
                td = re.findall('(\d+-\d+-\d+)', tds)[0]
            except:
                tds = tr.find_all("td")[-2].text.strip()
                if tds == '--':
                    continue
                td = re.findall('(\d+-\d+-\d+)', tds)[0]
            info = None
        tmp = [title, td, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    url = driver.current_url
    if '/zfcgwsjjpt/JyWeb/' in url:
        locator = (By.XPATH, '//div[@class="new_news_content"]/ul/li[1]//a | //div[@class="new_news_content"]/ul/li[1]/span[1]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "//td[@class='page_bar']")
            str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num = re.findall(r'/(\d+)', str)[0]
        except:
            num = 1
        driver.quit()
        return int(num)
    else:
        locator = (By.XPATH, '//li[@class="clearfloat"]/table/tbody/tr[2]/td/a')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, "//div[@class='mmggxlh']/a[last()-1]")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = int(str)
        driver.quit()
        return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='mid_content'] | //div[@class='content_all']")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('div', class_="main_con")
    if div == None:
        div = soup.find('div', class_="content_all")
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.yaggzy.org.cn/jyxx/jsgcZbgg",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_biangeng_gg",
     "http://www.yaggzy.org.cn/jyxx/jsgcBgtz",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_liubiao_zhongzhi_gg",
     "http://www.yaggzy.org.cn/jyxx/jsgcZzgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.yaggzy.org.cn/jyxx/jsgcpbjggs",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_zhonghxbiangeng_gg",
     "http://www.yaggzy.org.cn/jyxx/jsgcZbhxrbggs",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gglx':'评标结果变更公示'}), f2],

    ["gcjs_zhongbiao_gg",
     "http://www.yaggzy.org.cn/jyxx/jsgcZbjggs",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_jieguobiangeng_gg",
     "http://www.yaggzy.org.cn/jyxx/jsgcZbjgbg",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gglx':'中标结果变更公示'}), f2],

    ["gcjs_hetong_gg",
     "http://www.yaggzy.org.cn/jyxx/jsgcHtgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_liubiao_gg",
     "http://www.yaggzy.org.cn/jyxx/jsgcLbgs",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://www.yaggzy.org.cn/jyxx/zfcg/cggg",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_biangeng_gg",
     "http://www.yaggzy.org.cn/jyxx/zfcg/gzsx",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_zhong_liu_gg",
     "http://www.yaggzy.org.cn/jyxx/zfcg/zbjggs",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_wsjj_gg",
     "http://www.yaggzy.org.cn/zfcgwsjjpt/JyWeb/TradeInfo/JingJiaXinXiList?SubType=50000&SubType2=6010&Type=%E7%AB%9E%E4%BB%B7%E4%BF%A1%E6%81%AF",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx':'网上竞价'}), f2],

    ["zfcg_zhaobiao_wsjj_zhigou_gg",
     "http://www.yaggzy.org.cn/zfcgwsjjpt/JyWeb/TradeInfo/JingJiaXinXiList?SubType=50000&SubType2=6020&Type=%E7%AB%9E%E4%BB%B7%E4%BF%A1%E6%81%AF",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx':'网上竞价', 'zbfs':'直购'}), f2],

    ["zfcg_zhongbiao_wsjj_gg",
     "http://www.yaggzy.org.cn/zfcgwsjjpt/JyWeb/TradeInfo/JingJiaXinXiList?SubType=50000&SubType2=6030&Type=%E7%AB%9E%E4%BB%B7%E4%BF%A1%E6%81%AF",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx':'网上竞价'}), f2],

    ["zfcg_liubiao_wsjj_gg",
     "http://www.yaggzy.org.cn/zfcgwsjjpt/JyWeb/TradeInfo/JingJiaXinXiList?SubType=50000&SubType2=6040&Type=%E7%AB%9E%E4%BB%B7%E4%BF%A1%E6%81%AF",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx':'网上竞价'}), f2],

    ["zfcg_liubiao_zhongzhi_wsjj_gg",
     "http://www.yaggzy.org.cn/zfcgwsjjpt/JyWeb/TradeInfo/JingJiaXinXiList?SubType=50000&SubType2=6050&Type=%E7%AB%9E%E4%BB%B7%E4%BF%A1%E6%81%AF",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx':'网上竞价'}), f2],

    ["zfcg_gqita_yanshou_wsjj_gg",
     "http://www.yaggzy.org.cn/zfcgwsjjpt/JyWeb/TradeInfo/JingJiaXinXiList?SubType=50000&SubType2=6070&Type=%E7%AB%9E%E4%BB%B7%E4%BF%A1%E6%81%AF",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx': '网上竞价'}), f2],

    ["qsy_zhaobiao_gg",
     "http://www.yaggzy.org.cn/jyxx/qtjy/crgg",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx': '其他交易'}), f2],

    ["qsy_gqita_zhong_liu_gg",
     "http://www.yaggzy.org.cn/jyxx/qtjy/cjqr",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx': '其他交易'}), f2],

]



def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省雅安市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","sichuan","yaan"])




