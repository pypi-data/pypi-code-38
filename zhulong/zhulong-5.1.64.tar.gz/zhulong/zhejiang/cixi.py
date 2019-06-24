import random
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zhulong.util.etl import est_meta,est_html,add_info
from zhulong.util.fake_useragent import UserAgent

_name_="cixi"


columnid = None
unitid = None

def f1(driver, num):
    locator = (By.XPATH, "//table[@class='table-box']/tbody/tr[last()-1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='pagesite']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = re.findall(r'(\d+)/', st)[0]
    except:cnum=1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@class='table-box']/tbody/tr[last()-1]//a").get_attribute('href')[-15:]
        driver.execute_script("location.href=encodeURI('index_{}.jhtml?areaCode=330282');".format(num))
        locator = (By.XPATH, "//table[@class='table-box']/tbody/tr[last()-1]//a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table', class_='table-box').tbody
    lis = table.find_all('tr')
    data= []
    for li in lis[1:-1]:

        a = li.find("a")
        try:
            name = a['title'].strip()
        except:
            name = a.text.strip()

        link = a["href"].strip()
        if 'http' in link:
            href = link
        else:href ='http://cixi.bidding.gov.cn' + link
        ggstart_time = li.find_all("td")[-1].text.strip()
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//table[@class='table-box']/tbody/tr[last()-1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='pagesite']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = re.findall(r'/(\d+)页', st)[0]
    except:
        num = 1
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='content-box'][string-length()>40]")
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
    div = soup.find('div', class_="content-box")
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://cixi.bidding.gov.cn/cxxizbgg/index.jhtml?areaCode=330282",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_yuzhaobiao_gg",
     "http://cixi.bidding.gov.cn/gcjszbggygs/index.jhtml?areaCode=330282",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'工程建设招标文件预公示'}), f2],
    #
    ["gcjs_gqita_bian_bu_gg",
     "http://cixi.bidding.gov.cn/cxbcwj/index.jhtml?areaCode=330282",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://cixi.bidding.gov.cn/cxjjgs/index.jhtml?areaCode=330282",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiao_gg",
     "http://cixi.bidding.gov.cn/fhzbjggg/index.jhtml?areaCode=330282",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["zfcg_zhaobiao_gg",
     "http://cixi.bidding.gov.cn/zfcgcggg/index.jhtml?areaCode=330282",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhongbiao_gg",
     "http://cixi.bidding.gov.cn/zfcgcgjggs2/index.jhtml?areaCode=330282",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhaobiao_danyilaiyuan_gg",
     "http://cixi.bidding.gov.cn/zfcgdyly/index.jhtml?areaCode=330282",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'单一来源'}),f2],

    ["zfcg_yucai_gg",
     "http://cixi.bidding.gov.cn/cxcgwjhxqgs/index.jhtml?areaCode=330282",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["qsy_zhaobiao_gg",
     "http://cixi.bidding.gov.cn/cxjygg1/index.jhtml?areaCode=330282",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'其他公共资源(国企)'}), f2],

    ["qsy_zhongbiao_gg",
     "http://cixi.bidding.gov.cn/cxjygggs1/index.jhtml?areaCode=330282",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'其他公共资源(国企)'}), f2],


    ["jqita_zhaobiao_gg",
     "http://cixi.bidding.gov.cn/cxcggg1/index.jhtml?areaCode=330282",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'镇级平台(农交所)公告'}), f2],

    ["jqita_zhongbiao_gg",
     "http://cixi.bidding.gov.cn/cxcggs/index.jhtml?areaCode=330282",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'镇级平台(农交所)公告'}), f2],

    ["jqita_zhaobiao_gc_gg",
     "http://cixi.bidding.gov.cn/gczbgg/index.jhtml?areaCode=330282",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx': '镇级平台(农交所)公告', 'gglx':'工程招标公告'}), f2],

    ["jqita_zhongbiao_gc_gg",
     "http://cixi.bidding.gov.cn/gcjggs/index.jhtml?areaCode=330282",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx': '镇级平台(农交所)公告', 'gglx':'工程结果公告'}), f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="浙江省慈溪市",**args)
    est_html(conp,f=f3,**args)



# 网站变更：http://cixi.bidding.gov.cn/330282.html
# 更新日期：2019/6/24
if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.4.175","zhejiang","cixi"],pageloadtimeout=60)

    # for d in data:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     print(url)
    #     driver.get(url)
    #     df = f2(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #     for i in range(1, 5):
    #         df=f1(driver, i)
    #         print(df.values)
    #         for f in df[2].values:
    #             d = f3(driver, f)
    #             print(d)